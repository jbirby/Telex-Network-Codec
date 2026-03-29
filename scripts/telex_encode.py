#!/usr/bin/env python3
"""
Telex Encoder
Encodes text into Telex audio WAV files using ITA2 Baudot code at 50 baud.

Usage:
    python3 telex_encode.py <message_text_or_file> <output.wav> [--answerback CODE] [--with-handshake]
"""

import sys
import argparse
import os
from pathlib import Path
import numpy as np

from telex_common import (
    FSKModulator,
    text_to_baudot,
    baudot_to_text,
    format_telex_message,
    generate_answerback,
    generate_dial_tone,
    generate_answerback_signal,
    generate_ga_signal,
    write_wav,
    TelexParams,
)


def encode_message(
    text,
    answerback=None,
    with_handshake=False,
    sample_rate=8000,
):
    """
    Encode text to telex audio.

    Args:
        text: Message text to encode
        answerback: Optional answerback code. If None, auto-generates.
        with_handshake: If True, include connection handshake simulation
        sample_rate: Audio sample rate (default 8000 Hz)

    Returns:
        Audio samples as numpy array
    """
    samples = []

    if with_handshake:
        # Dial tone (caller side)
        dial = generate_dial_tone(duration=2, sample_rate=sample_rate)
        samples.append(dial)

        # Silence while dialing
        silence = np.zeros(int(1 * sample_rate))
        samples.append(silence)

        # Called machine's answerback
        if answerback is None:
            answerback = generate_answerback()

        answerback_audio = generate_answerback_signal(
            answerback, sample_rate=sample_rate
        )
        samples.append(answerback_audio)

        # Silence
        samples.append(np.zeros(int(0.5 * sample_rate)))

        # GA signal (go ahead)
        ga = generate_ga_signal(sample_rate=sample_rate)
        samples.append(ga)

        # Silence before message
        samples.append(np.zeros(int(0.5 * sample_rate)))

    # Format message
    formatted = format_telex_message(text, sender=answerback or "")

    # Encode message
    modulator = FSKModulator(sample_rate=sample_rate)
    baudot_codes = text_to_baudot(formatted)
    message_audio = modulator.modulate_codes(baudot_codes)
    samples.append(message_audio)

    # Post-message silence
    samples.append(np.zeros(int(0.5 * sample_rate)))

    # Concatenate all samples
    return np.concatenate(samples)


def main():
    parser = argparse.ArgumentParser(
        description="Encode text as Telex audio WAV file"
    )
    parser.add_argument(
        "input",
        help="Text message or file containing message",
    )
    parser.add_argument(
        "output",
        help="Output WAV file",
    )
    parser.add_argument(
        "--answerback",
        default=None,
        help="Telex answerback code (e.g., TLX001). Auto-generated if not provided.",
    )
    parser.add_argument(
        "--with-handshake",
        action="store_true",
        help="Include connection handshake (dial tone, answerback exchange, GA signal)",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=8000,
        help="Audio sample rate in Hz (default 8000)",
    )

    args = parser.parse_args()

    # Read input
    if os.path.isfile(args.input):
        with open(args.input, "r") as f:
            text = f.read()
    else:
        text = args.input

    if not text.strip():
        print("Error: Empty message", file=sys.stderr)
        sys.exit(1)

    # Encode
    print(f"Encoding message: {text[:50]}...", file=sys.stderr)
    audio = encode_message(
        text,
        answerback=args.answerback,
        with_handshake=args.with_handshake,
        sample_rate=args.sample_rate,
    )

    # Write output
    write_wav(args.output, audio, sample_rate=args.sample_rate)
    print(f"Wrote {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
