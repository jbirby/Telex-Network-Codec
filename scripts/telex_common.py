"""
Telex Network Signaling Module
Implements ITA2 Baudot code, FSK modulation/demodulation, and telex conventions.
Telex: landline teleprinter network (1930s-2000s), 50 baud ITU-T standard
"""

import numpy as np
import struct
from enum import IntEnum
import random
import string


# ============================================================================
# ITA2 Baudot Code (5-bit character encoding)
# ============================================================================

class BaudotMode(IntEnum):
    """Baudot character set selection"""
    LTRS = 0  # Letters mode
    FIGS = 1  # Figures mode


# ITA2 Baudot character tables (same as RTTY but context differs)
BAUDOT_LTRS = {
    0x00: 'Ø',  # Null
    0x01: 'E',
    0x02: '\n', # Line feed
    0x03: 'A',
    0x04: ' ',  # Space
    0x05: 'BEL', # Bell (rings the telex machine)
    0x06: 'B',
    0x07: '?',  # Unassigned
    0x08: 'C',
    0x09: 'WRU', # Who aRe yoU? (triggers answerback)
    0x0A: 'D',
    0x0B: '?',  # Unassigned
    0x0C: 'E',
    0x0D: '\r', # Carriage return
    0x0E: 'F',
    0x0F: '?',  # Unassigned
    0x10: 'G',
    0x11: 'H',
    0x12: 'I',
    0x13: 'J',
    0x14: 'K',
    0x15: 'L',
    0x16: 'M',
    0x17: 'N',
    0x18: 'O',
    0x19: 'P',
    0x1A: 'Q',
    0x1B: 'R',
    0x1C: 'S',
    0x1D: 'T',
    0x1E: 'U',
    0x1F: 'V',
    0x20: 'W',
    0x21: 'X',
    0x22: 'Y',
    0x23: 'Z',
    0x24: '?',  # Unassigned
    0x25: '?',  # Unassigned
    0x26: '?',  # Unassigned
    0x27: '?',  # Unassigned
    0x28: '?',  # Unassigned
    0x29: '?',  # Unassigned
    0x2A: '?',  # Unassigned
    0x2B: 'FIGS', # Switch to figures
    0x2C: '?',  # Unassigned
    0x2D: '?',  # Unassigned
    0x2E: '?',  # Unassigned
    0x2F: 'LTRS', # Switch to letters
    0x30: '?',
    0x31: '?',
}

BAUDOT_FIGS = {
    0x00: 'Ø',  # Null
    0x01: '3',
    0x02: '\n', # Line feed
    0x03: '-',  # Hyphen/dash
    0x04: ' ',  # Space
    0x05: 'BEL', # Bell
    0x06: '?',
    0x07: '?',
    0x08: '(',
    0x09: 'WRU', # Who aRe yoU?
    0x0A: '$',
    0x0B: '?',
    0x0C: '&',
    0x0D: '\r', # Carriage return
    0x0E: '!',
    0x0F: '?',
    0x10: '?',
    0x11: '#',
    0x12: '8',
    0x13: '\'', # Apostrophe
    0x14: '(',
    0x15: ')',
    0x16: '?',
    0x17: ',',
    0x18: '9',
    0x19: '0',
    0x1A: '1',
    0x1B: '4',
    0x1C: '?',
    0x1D: '5',
    0x1E: '7',
    0x1F: '=',
    0x20: '2',
    0x21: '//',  # Slash
    0x22: '6',
    0x23: '+',
    0x24: '?',
    0x25: '?',
    0x26: '?',
    0x27: '?',
    0x28: '?',
    0x29: '?',
    0x2A: '?',
    0x2B: 'FIGS', # Stay in figures
    0x2C: '?',
    0x2D: '?',
    0x2E: '?',
    0x2F: 'LTRS', # Switch to letters
    0x30: '?',
    0x31: '?',
}

# Build reverse mapping (text -> code)
def _build_reverse_map(baudot_table):
    """Build char -> code mapping, handling mode shifts"""
    reverse = {}
    for code, char in baudot_table.items():
        if char not in ('?', 'Ø'):
            if char not in reverse:
                reverse[char] = code
    return reverse

BAUDOT_LTRS_REV = _build_reverse_map(BAUDOT_LTRS)
BAUDOT_FIGS_REV = _build_reverse_map(BAUDOT_FIGS)


def baudot_char_to_code(char, current_mode=BaudotMode.LTRS):
    """
    Convert a character to Baudot code, returning (code, new_mode).
    Returns None if char cannot be encoded.
    """
    # Try current mode first
    if current_mode == BaudotMode.LTRS:
        if char in BAUDOT_LTRS_REV:
            return (BAUDOT_LTRS_REV[char], BaudotMode.LTRS)
        # Try figures mode
        if char in BAUDOT_FIGS_REV:
            return (0x2B, current_mode)  # FIGS switch code, then figures
    else:  # FIGS mode
        if char in BAUDOT_FIGS_REV:
            return (BAUDOT_FIGS_REV[char], BaudotMode.FIGS)
        # Try letters mode
        if char in BAUDOT_LTRS_REV:
            return (0x2F, current_mode)  # LTRS switch code, then letters

    return None


def baudot_code_to_char(code, mode=BaudotMode.LTRS):
    """
    Convert Baudot code to character in given mode.
    Returns character string and updated mode.
    """
    if mode == BaudotMode.LTRS:
        table = BAUDOT_LTRS
    else:
        table = BAUDOT_FIGS

    char = table.get(code, '?')

    # Handle mode switches
    if char == 'FIGS':
        return '', BaudotMode.FIGS
    elif char == 'LTRS':
        return '', BaudotMode.LTRS

    return char, mode


def text_to_baudot(text):
    """
    Convert text string to list of Baudot codes.
    Includes automatic mode switching.
    """
    codes = []
    mode = BaudotMode.LTRS
    text = text.upper()

    for char in text:
        result = baudot_char_to_code(char, mode)
        if result is None:
            continue

        code, new_mode = result

        # Add mode switch if needed
        if new_mode != mode and code in (0x2B, 0x2F):
            codes.append(code)
            mode = new_mode
        elif new_mode != mode:
            # Need to insert mode switch first
            if new_mode == BaudotMode.FIGS:
                codes.append(0x2B)
            else:
                codes.append(0x2F)
            mode = new_mode
            codes.append(code)
        else:
            codes.append(code)

    return codes


def baudot_to_text(codes):
    """
    Convert list of Baudot codes to text string.
    Handles mode switching automatically.
    """
    text = []
    mode = BaudotMode.LTRS

    for code in codes:
        char, new_mode = baudot_code_to_char(code, mode)
        mode = new_mode
        if char and char not in ('', '\x00'):
            text.append(char)

    return ''.join(text)


# ============================================================================
# Telex Network Parameters
# ============================================================================

class TelexParams:
    """Telex network standard parameters (ITU-T)"""

    BAUD_RATE = 50  # International standard
    BITS_PER_CHAR = 5  # Baudot data bits
    START_BITS = 1
    STOP_BITS = 1.5  # 1.5 stop bits
    TOTAL_BITS = START_BITS + BITS_PER_CHAR + STOP_BITS  # 7.5 bits

    MARK_FREQ = 1400  # Hz (binary 0)
    SPACE_FREQ = 1800  # Hz (binary 1)
    FREQ_SHIFT = SPACE_FREQ - MARK_FREQ  # 400 Hz shift

    # Character duration at 50 baud
    CHAR_DURATION = TOTAL_BITS / BAUD_RATE  # 0.15 seconds = 150ms


# ============================================================================
# FSK Modulation/Demodulation
# ============================================================================

class FSKModulator:
    """FSK (Frequency Shift Keying) modulator for Telex"""

    def __init__(
        self,
        baud_rate=TelexParams.BAUD_RATE,
        mark_freq=TelexParams.MARK_FREQ,
        space_freq=TelexParams.SPACE_FREQ,
        sample_rate=8000,
    ):
        self.baud_rate = baud_rate
        self.mark_freq = mark_freq
        self.space_freq = space_freq
        self.sample_rate = sample_rate
        self.samples_per_bit = sample_rate / baud_rate

    def modulate_bit(self, bit, duration_bits=1):
        """
        Modulate a single bit (or multiple bits of same value).
        Returns audio samples.
        """
        freq = self.space_freq if bit else self.mark_freq
        num_samples = int(self.samples_per_bit * duration_bits)
        t = np.arange(num_samples) / self.sample_rate
        return np.sin(2 * np.pi * freq * t)

    def modulate_byte(self, byte_val):
        """
        Modulate a Baudot byte (5 data bits) with start and stop bits.
        Format: 1 start bit (space), 5 data bits (LSB first), 1.5 stop bits (mark)
        """
        samples = []

        # Start bit (space = 1)
        samples.append(self.modulate_bit(1, 1))

        # Data bits (LSB first)
        for i in range(5):
            bit = (byte_val >> i) & 1
            samples.append(self.modulate_bit(bit, 1))

        # Stop bits (mark = 0, 1.5 bits)
        samples.append(self.modulate_bit(0, 1.5))

        return np.concatenate(samples)

    def modulate_codes(self, baudot_codes):
        """Modulate a list of Baudot codes to audio"""
        samples = []
        for code in baudot_codes:
            samples.append(self.modulate_byte(code))
        return np.concatenate(samples)


class FSKDemodulator:
    """FSK demodulator for Telex"""

    def __init__(
        self,
        baud_rate=TelexParams.BAUD_RATE,
        mark_freq=TelexParams.MARK_FREQ,
        space_freq=TelexParams.SPACE_FREQ,
        sample_rate=8000,
    ):
        self.baud_rate = baud_rate
        self.mark_freq = mark_freq
        self.space_freq = space_freq
        self.sample_rate = sample_rate
        self.samples_per_bit = sample_rate / baud_rate

    def demodulate_bit(self, samples):
        """Detect if a bit period contains mark or space frequency"""
        if len(samples) == 0:
            return 0

        t = np.arange(len(samples)) / self.sample_rate

        # Create sine and cosine basis functions for correlation
        mark_sine = np.sin(2 * np.pi * self.mark_freq * t)
        mark_cosine = np.cos(2 * np.pi * self.mark_freq * t)
        space_sine = np.sin(2 * np.pi * self.space_freq * t)
        space_cosine = np.cos(2 * np.pi * self.space_freq * t)

        # Correlate with both sin and cos for robustness
        mark_i = np.sum(samples * mark_sine)
        mark_q = np.sum(samples * mark_cosine)
        mark_power = mark_i ** 2 + mark_q ** 2

        space_i = np.sum(samples * space_sine)
        space_q = np.sum(samples * space_cosine)
        space_power = space_i ** 2 + space_q ** 2

        return 1 if space_power > mark_power else 0

    def demodulate_byte(self, samples):
        """
        Demodulate a byte period from audio.
        Returns the 5-bit data byte (bits extracted LSB first after start/stop).
        """
        bit_samples = int(self.samples_per_bit)
        byte_val = 0

        # Skip start bit
        pos = bit_samples

        # Extract 5 data bits (LSB first)
        for i in range(5):
            bit_samples_slice = samples[pos : pos + bit_samples]
            if len(bit_samples_slice) < bit_samples:
                break
            bit = self.demodulate_bit(bit_samples_slice)
            byte_val |= (bit << i)
            pos += bit_samples

        return byte_val

    def demodulate_codes(self, audio_samples):
        """Demodulate audio to list of Baudot codes with frame sync"""
        if len(audio_samples) == 0:
            return []

        codes = []
        bit_samples = int(self.samples_per_bit)

        # Each character is 7.5 bits
        char_bits = TelexParams.TOTAL_BITS
        char_samples = int(char_bits * bit_samples)

        # Try to find frame sync by looking for start bit (1) followed by data bits
        # Skip initial silence/noise
        threshold = np.mean(np.abs(audio_samples)) * 0.3
        start_pos = 0
        for i in range(len(audio_samples) - char_samples):
            if np.mean(np.abs(audio_samples[i:i+bit_samples])) > threshold:
                start_pos = i
                break

        pos = start_pos
        while pos + char_samples <= len(audio_samples):
            char_audio = audio_samples[pos : pos + char_samples]
            code = self.demodulate_byte(char_audio)
            codes.append(code)
            pos += char_samples

        return codes


# ============================================================================
# Telex-Specific Features
# ============================================================================

def generate_answerback(prefix="TLX", machine_id=None):
    """
    Generate a telex answerback code (like a caller ID).
    Typically: 2-4 letters + optional digits
    Example: "TLX001" or "NEW"
    """
    if machine_id is None:
        machine_id = random.randint(0, 999)

    answerback = f"{prefix}{machine_id:03d}"
    return answerback.upper()


def format_telex_message(text, routing_prefix="", sender="", reference=""):
    """
    Format text as a telex message with conventions.
    Telex conventions: uppercase, abbreviations, routing info.
    """
    # Format: [ROUTING] [SENDER] [DATE] [REF] [MESSAGE] [NNNN]
    lines = []

    if routing_prefix:
        lines.append(f"+++{routing_prefix}")

    if sender:
        lines.append(f"TLX: {sender}")

    # Message body
    lines.append(text.upper())

    # End marker
    lines.append("+++")

    return "\n".join(lines)


def extract_telex_message(text):
    """Extract message body from formatted telex"""
    lines = text.split("\n")
    message_lines = []
    in_message = False

    for line in lines:
        if line.startswith("+++"):
            continue
        if line.startswith("TLX:"):
            continue
        if line.startswith("NR"):
            continue
        if line.startswith("REF"):
            continue
        message_lines.append(line.strip())

    return "\n".join(message_lines).strip()


# ============================================================================
# Connection Handshake Simulation
# ============================================================================

def generate_dial_tone(duration=2, sample_rate=8000):
    """
    Generate a dialtone (350 + 440 Hz).
    Used at start of connection simulation.
    """
    t = np.arange(int(duration * sample_rate)) / sample_rate
    dial = 0.3 * (
        np.sin(2 * np.pi * 350 * t) + np.sin(2 * np.pi * 440 * t)
    )
    return dial


def generate_answerback_signal(answerback, sample_rate=8000, include_wru=True):
    """
    Generate answerback signal (text transmitted at telex speed).
    This is what the called subscriber's machine transmits back.
    """
    modulator = FSKModulator(sample_rate=sample_rate)

    # If include_wru, start with WRU character
    codes = []
    if include_wru:
        codes.append(0x09)  # WRU code

    # Then the answerback text
    codes.extend(text_to_baudot(answerback))

    # CR+LF to end
    codes.extend([0x0D, 0x0A])

    return modulator.modulate_codes(codes)


def generate_ga_signal(sample_rate=8000):
    """
    Generate a GA (Go Ahead) signal.
    Typically a brief tone or character sequence.
    For simplicity: silence or a single character sequence.
    """
    # GA can be represented as a line feed + carriage return
    modulator = FSKModulator(sample_rate=sample_rate)
    codes = [0x0D, 0x0A]  # CR + LF
    return modulator.modulate_codes(codes)


# ============================================================================
# WAV File I/O
# ============================================================================

def write_wav(filename, samples, sample_rate=8000, bits=16):
    """
    Write audio samples to WAV file.
    """
    # Normalize to [-1, 1]
    max_val = np.max(np.abs(samples))
    if max_val > 0:
        samples = samples / max_val * 0.95

    # Convert to integer samples
    if bits == 16:
        max_int = 32767
        samples_int = np.clip(samples * max_int, -max_int, max_int).astype(
            np.int16
        )
    else:
        max_int = 127
        samples_int = np.clip(samples * max_int, -max_int, max_int).astype(
            np.int8
        )

    # WAV file format
    num_samples = len(samples_int)
    num_channels = 1
    byte_rate = sample_rate * num_channels * (bits // 8)
    block_align = num_channels * (bits // 8)

    with open(filename, "wb") as f:
        # RIFF header
        f.write(b"RIFF")
        f.write(
            struct.pack(
                "<I", 36 + num_samples * num_channels * (bits // 8)
            )
        )
        f.write(b"WAVE")

        # fmt sub-chunk
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))  # Subchunk1Size
        f.write(struct.pack("<H", 1))  # AudioFormat (1=PCM)
        f.write(struct.pack("<H", num_channels))
        f.write(struct.pack("<I", sample_rate))
        f.write(struct.pack("<I", byte_rate))
        f.write(struct.pack("<H", block_align))
        f.write(struct.pack("<H", bits))

        # data sub-chunk
        f.write(b"data")
        f.write(
            struct.pack(
                "<I", num_samples * num_channels * (bits // 8)
            )
        )
        f.write(samples_int.tobytes())


def read_wav(filename):
    """
    Read audio samples from WAV file.
    Returns (samples, sample_rate)
    """
    with open(filename, "rb") as f:
        # Read RIFF header
        riff_tag = f.read(4)
        if riff_tag != b"RIFF":
            raise ValueError("Not a valid WAV file")

        file_size = struct.unpack("<I", f.read(4))[0]
        wave_tag = f.read(4)
        if wave_tag != b"WAVE":
            raise ValueError("Not a valid WAV file")

        # Find fmt chunk
        while True:
            chunk_id = f.read(4)
            if not chunk_id:
                break

            chunk_size = struct.unpack("<I", f.read(4))[0]

            if chunk_id == b"fmt ":
                audio_format = struct.unpack("<H", f.read(2))[0]
                num_channels = struct.unpack("<H", f.read(2))[0]
                sample_rate = struct.unpack("<I", f.read(4))[0]
                byte_rate = struct.unpack("<I", f.read(4))[0]
                block_align = struct.unpack("<H", f.read(2))[0]
                bits_per_sample = struct.unpack("<H", f.read(2))[0]

                # Skip remaining fmt data
                f.read(chunk_size - 16)

            elif chunk_id == b"data":
                num_samples = chunk_size // (num_channels * bits_per_sample // 8)
                sample_data = f.read(chunk_size)

                # Convert to float samples in [-1, 1]
                if bits_per_sample == 16:
                    samples = np.frombuffer(sample_data, dtype=np.int16).astype(
                        np.float32
                    )
                    samples /= 32768.0
                else:
                    samples = np.frombuffer(sample_data, dtype=np.int8).astype(
                        np.float32
                    )
                    samples /= 128.0

                return samples, sample_rate
            else:
                f.read(chunk_size)

    raise ValueError("Could not find data chunk in WAV file")
