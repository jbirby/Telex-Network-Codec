#!/usr/bin/env python3
"""
Telex Decoder
Decodes Telex audio WAV files back to text using ITA2 Baudot code at 50 baud.

Usage:
    python3 telex_decode.py <input.wav> [output.txt]
"""

import sys
import argparse
import os
from pathlib import Path
import numpy as np

from telex_common import (
    FSKDemodulator,
    baudot_to_text,
    extract_telex_message,
    read_wav,
    TelexParams,
)


def decode_audio(audio_samples, sample_rate=8000):
    """
    Decode telex audio to text.

    Args:
        audio_samples: Audio samples as numpy array
        sample_rate: Sample rate of audio

    Returns:
        Decoded text string
    """
    demodulator = FSKDemodulator(sample_rate=sample_rate)

    # Demodulate to Baudot codes
    codes = demodulator.demodulate_codes(audio_samples)

    # Convert to text
    text = baudot_to_text(codes)

    return text


def identify_answerback(text):
    """
    Try to identify answerback sequence in decoded text.
    Answerback typically appears near start and ends with CR+LF.
    """
    lines = text.split("\n")
    for i, line in enumerate(lines[:5]):  # Check first 5 lines
        line = line.strip()
        if len(line) >= 3 and len(line) <= 10:
            if line.isupper():
                return line
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Decode Telex WAV file back to text"
    )
    parser.add_argument(
        "input",
        help="Input WAV file",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="Output text file (optional, prints to stdout if not provided)",
    )
    parser.add_argument(
        "--show-answerback",
        action="store_true",
        help="Identify and display answerback code",
    )

    args = parser.parse_args()

    # Read WAV file
    if not os.path.isfile(args.input):
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"Reading {args.input}...", file=sys.stderr)
    audio_samples, sample_rate = read_wav(args.input)

    # Decode
    print(f"Decoding at {sample_rate} Hz...", file=sys.stderr)
    text = decode_audio(audio_samples, sample_rate=sample_rate)

    # Extract message (remove formatting)
    message = extract_telex_message(text)

    # Show answerback if requested
    if args.show_answerback:
        answerback = identify_answerback(text)
        if answerback:
            print(f"Answerback: {answerback}", file=sys.stderr)

    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(message)
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        print(message)


if __name__ == "__main__":
    main()
