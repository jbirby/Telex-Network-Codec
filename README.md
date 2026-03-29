# Telex Network Codec

Encode text into Telex network audio WAV files and decode Telex recordings back into text using ITA2 Baudot code at 50 baud with FSK modulation.

## Overview

This skill implements the Telex network codec, enabling simulation and audio transmission of messages over the historical landline teleprinter network that operated from the 1930s through the 2000s.

**Telex** (Teleprinter Exchange) was a global network of electromechanical teleprinters connected via dedicated phone lines. Each telex machine had:
- A unique answerback code (like a caller ID)
- Real-time typed message transmission
- Automatic routing via international numbering
- Built-in features like the WRU (Who aRe yoU?) signal to request answerback identification

## Telex vs RTTY: Key Differences

| Aspect | RTTY | Telex |
|--------|------|-------|
| **Medium** | Radio (HF/VHF) | Landline (phone network) |
| **Baud Rate** | 45.45 (amateur) or 50/75/100 (commercial) | 50 (ITU-T standard) |
| **Encoding** | ITA2 Baudot code | ITA2 Baudot code |
| **FSK Shift** | 170 Hz (amateur), 425 Hz (commercial) | 400 Hz (typical TDM carrier) |
| **Tones** | Varies by mode | Mark 1400 Hz, Space 1800 Hz |
| **Signaling** | Limited | Rich (answerback, WRU, GA, routing) |
| **Format** | Free-form text | Formal message structure with routing |

## Technical Specifications

### Baudot Code (ITA2)
- **5-bit character encoding** (32 possible characters)
- Two character sets: **LTRS** (letters) and **FIGS** (figures)
- Mode switching via 0x2B (FIGS) and 0x2F (LTRS) codes
- Special characters for control/signaling

### Modulation Parameters
- **Baud Rate**: 50 baud (international ITU-T standard)
- **Bits per Character**: 1 start + 5 data + 1.5 stop = 7.5 bits
- **Character Duration**: 150 milliseconds
- **FSK Frequencies**: Mark 1400 Hz, Space 1800 Hz (400 Hz shift)
- **Audio Format**: 16-bit mono WAV at 8000 Hz sample rate

### Telex-Specific Features

#### Answerback
Each telex machine has a unique answerback code (2-4 alphanumeric characters). When a calling machine sends the WRU (Who aRe yoU?) character (0x09), the called machine automatically responds with its answerback.

#### WRU Signal
Baudot code 0x09 in FIGS mode triggers answerback transmission. Used to identify the machine at the other end.

#### BEL Character
Baudot code 0x05 in FIGS mode rings the machine's bell, alerting the operator.

#### Message Format
Standard telex messages follow conventions:
```
+++ROUTING_PREFIX
TLX: SENDER_ANSWERBACK
ACTUAL MESSAGE TEXT HERE
+++
```

#### Connection Handshake
A typical telex call follows this sequence:
1. Caller initiates connection (dial tone)
2. Called machine sends answerback (WRU + code)
3. Caller acknowledges (GA signal)
4. Message transmission begins
5. Message ends with "++" marker

#### International Telex Numbering
Telex numbers typically follow the format:
- Country code (1-4 digits)
- Regional code
- Machine number
- Example: US 212-555-0100

## Installation

### Requirements
- Python 3.7+
- NumPy

### Setup
```bash
cd telex/scripts
pip install numpy
```

## Usage

### Encoding Text to Telex Audio

#### Basic Usage
```bash
python3 telex_encode.py "HELLO WORLD" output.wav
```

#### With Answerback Code
```bash
python3 telex_encode.py "HELLO WORLD" output.wav --answerback TLX001
```

#### With Connection Handshake
```bash
python3 telex_encode.py "HELLO WORLD" output.wav --with-handshake
```

#### From File
```bash
python3 telex_encode.py message.txt output.wav
```

#### Full Example
```bash
python3 telex_encode.py "CALLING NEW YORK TELEX" output.wav \
    --answerback NEW \
    --with-handshake
```

### Decoding Telex Audio to Text

#### Basic Usage
```bash
python3 telex_decode.py recording.wav
```

#### Save to File
```bash
python3 telex_decode.py recording.wav decoded_message.txt
```

#### Show Answerback
```bash
python3 telex_decode.py recording.wav --show-answerback
```

## Examples

### Example 1: Simple Message
```bash
$ python3 telex_encode.py "HELLO THIS IS A TEST" hello.wav
$ python3 telex_decode.py hello.wav
HELLO THIS IS A TEST
```

### Example 2: Simulated Telex Call
```bash
$ python3 telex_encode.py "URGENT MESSAGE STOP PLEASE ADVISE" \
    call.wav --answerback NYC --with-handshake
$ python3 telex_decode.py call.wav --show-answerback
Answerback: NYC
URGENT MESSAGE STOP PLEASE ADVISE
```

### Example 3: Batch Processing
```bash
for msg in msg1.txt msg2.txt msg3.txt; do
    python3 telex_encode.py "$msg" "${msg%.txt}.wav" --answerback TLX
done
```

## Implementation Details

### FSK Modulation
The codec uses Frequency Shift Keying (FSK) to encode binary data:
- Binary 1 (space) → 1800 Hz sine wave
- Binary 0 (mark) → 1400 Hz sine wave
- Baud rate determines duration of each bit

### Baudot Decoding
Two-phase decoding:
1. **FSK demodulation**: Audio → binary bit stream
2. **Baudot decoding**: 5-bit codes → character text with mode awareness

### Character Mode Switching
The codec automatically handles switching between LTRS (letters) and FIGS (figures) modes based on the characters in the message.

### Error Handling
- Invalid Baudot codes default to "?"
- Mode switches are implicit (no manual selection needed)
- Malformed audio may produce garbled output (add noise robustness in future)

## File Structure

```
telex/
├── README.md                 # This file
├── SKILL.md                  # Skill metadata
└── scripts/
    ├── telex_common.py       # Shared module (Baudot, FSK, answerback)
    ├── telex_encode.py       # CLI encoder
    ├── telex_decode.py       # CLI decoder
    └── test_roundtrip.py     # Roundtrip tests
```

## Testing

Run the roundtrip test to verify encode/decode accuracy:
```bash
python3 scripts/test_roundtrip.py
```

Output:
```
============================================================
Telex Codec Roundtrip Tests
============================================================

Testing Baudot encoding/decoding...
  ✓ 'HELLO WORLD' -> 11 codes -> 'HELLO WORLD'
  ✓ 'TELEX MACHINE' -> 13 codes -> 'TELEX MACHINE'
  ...

Testing FSK modulation/demodulation...
  Modulated 6 codes to 7200 samples
  Demodulated back with 100.0% code accuracy
  ✓ FSK modulation/demodulation working

Testing WAV file I/O...
  Wrote 16044 bytes to /tmp/.../test.wav
  Read 8000 samples at 8000 Hz
  ✓ Sample rate preserved
  ✓ Sample count reasonable

Testing full message encode/decode...
  Encoded 'HELLO TELEX WORLD' to 25200 samples
  Decoded to 'HELLO TELEX WORLD'
  ✓ Full roundtrip successful

============================================================
Tests complete
============================================================
```

## History

### Telex Network Timeline
- **1930s**: First mechanical teleprinters connect via dedicated lines
- **1950s-1960s**: Automated switching networks (ITA/ITT)
- **1970s-1980s**: Golden age; telex becomes standard for international business
- **1990s**: Gradual decline as email emerges
- **2000s**: Major carriers shut down services; fully phased out by 2013

### Technical Standards
- **ITU-T V.14**: Asynchronous/synchronous conversion
- **ITU-T V.23**: 600/1200 baud modem
- **ITA2**: 5-bit Baudot code (same as RTTY)
- **50 baud**: International standard baudrate for telex

## Related Projects

- **RTTY Codec**: For radio-based radioteletype (45.45/50/75/100 baud, variable shift)
- **FAX Codec**: For facsimile transmission (T.4 compression, V.27ter modulation)
- **SSTV Codec**: For slow-scan television (amateur radio picture transmission)
- **APT Codec**: For NOAA satellite picture transmission

## License

MIT License. See LICENSE file for details.

## Future Enhancements

- Noise robustness (Viterbi decoding, error correction)
- Multi-tone detection for improved demodulation
- Tape archive simulation (WOM format support)
- Advanced answerback validation
- International character set support
- Real telex dial tone simulation
- Connection state machine simulation

## References

- ITU-T T.50: International Reference Alphabet (ITA) and Morse Code
- ITU-T V.14: Asynchronous to Synchronous Conversion
- CCITT Orange Book: Telex Network Technical Details
- Radioteletype Operation Manual
