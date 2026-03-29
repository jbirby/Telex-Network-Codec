#!/usr/bin/env python3
"""
Roundtrip test for Telex codec.
Tests encoding -> decoding to verify accuracy.
"""

import sys
import os
import tempfile
from pathlib import Path
import numpy as np

# Add scripts dir to path
sys.path.insert(0, os.path.dirname(__file__))

from telex_common import (
    text_to_baudot,
    baudot_to_text,
    FSKModulator,
    FSKDemodulator,
    write_wav,
    read_wav,
    TelexParams,
)


def test_baudot_encoding():
    """Test Baudot code encoding/decoding"""
    print("Testing Baudot encoding/decoding...")

    test_strings = [
        "HELLO WORLD",
        "TELEX MACHINE",
        "THIS IS A TEST",
        "QSY 1400 HZ",
    ]

    for text in test_strings:
        # Encode text to Baudot codes
        codes = text_to_baudot(text)

        # Decode back to text
        decoded = baudot_to_text(codes)

        # Normalize for comparison (remove extra spaces, etc)
        original_clean = " ".join(text.split()).upper()
        decoded_clean = " ".join(decoded.split()).upper()

        match = original_clean == decoded_clean
        status = "✓" if match else "✗"
        print(f"  {status} '{text}' -> {len(codes)} codes -> '{decoded_clean}'")

        if not match:
            print(f"      Original: {original_clean}")
            print(f"      Decoded:  {decoded_clean}")


def test_fsk_modulation():
    """Test FSK modulation and demodulation"""
    print("\nTesting FSK modulation/demodulation...")

    modulator = FSKModulator()
    demodulator = FSKDemodulator()

    test_codes = [0x05, 0x09, 0x0D, 0x0A, 0x01, 0x03]  # Some control codes

    # Modulate
    audio = modulator.modulate_codes(test_codes)

    # Demodulate
    decoded_codes = demodulator.demodulate_codes(audio)

    # Check if at least some codes match (demodulation is imperfect)
    matches = sum(1 for c, d in zip(test_codes, decoded_codes[:len(test_codes)]) if c == d)
    accuracy = matches / len(test_codes) * 100

    print(f"  Modulated {len(test_codes)} codes to {len(audio)} samples")
    print(f"  Demodulated back with {accuracy:.1f}% code accuracy")

    if accuracy >= 80:
        print("  ✓ FSK modulation/demodulation working")
    else:
        print("  ✗ FSK modulation/demodulation poor accuracy")


def test_wav_roundtrip():
    """Test WAV file write/read roundtrip"""
    print("\nTesting WAV file I/O...")

    with tempfile.TemporaryDirectory() as tmpdir:
        wav_file = os.path.join(tmpdir, "test.wav")

        # Create test audio
        duration = 0.5  # seconds
        sample_rate = 8000
        freq = 1400
        t = np.arange(int(duration * sample_rate)) / sample_rate
        test_audio = np.sin(2 * np.pi * freq * t)

        # Write WAV
        write_wav(wav_file, test_audio, sample_rate=sample_rate)
        print(f"  Wrote {os.path.getsize(wav_file)} bytes to {wav_file}")

        # Read WAV
        read_audio, read_rate = read_wav(wav_file)
        print(f"  Read {len(read_audio)} samples at {read_rate} Hz")

        # Check
        if read_rate == sample_rate:
            print("  ✓ Sample rate preserved")
        else:
            print(f"  ✗ Sample rate changed: {sample_rate} -> {read_rate}")

        if len(read_audio) >= len(test_audio) * 0.95:
            print("  ✓ Sample count reasonable")
        else:
            print(f"  ✗ Sample count unexpected")


def test_full_message_encode_decode():
    """Test full message encoding and decoding"""
    print("\nTesting full message encode/decode...")

    test_message = "HELLO TELEX WORLD"

    with tempfile.TemporaryDirectory() as tmpdir:
        wav_file = os.path.join(tmpdir, "message.wav")

        # Encode
        modulator = FSKModulator()
        codes = text_to_baudot(test_message)
        audio = modulator.modulate_codes(codes)

        write_wav(wav_file, audio)
        print(f"  Encoded '{test_message}' to {len(audio)} samples")

        # Decode
        read_audio, sample_rate = read_wav(wav_file)
        demodulator = FSKDemodulator()
        decoded_codes = demodulator.demodulate_codes(read_audio)
        decoded_text = baudot_to_text(decoded_codes)

        print(f"  Decoded to '{decoded_text}'")

        # Compare
        original_clean = " ".join(test_message.split()).upper()
        decoded_clean = " ".join(decoded_text.split()).upper()

        if original_clean == decoded_clean:
            print("  ✓ Full roundtrip successful")
        else:
            print(f"  ✗ Mismatch:")
            print(f"      Original: {original_clean}")
            print(f"      Decoded:  {decoded_clean}")


def main():
    print("=" * 60)
    print("Telex Codec Roundtrip Tests")
    print("=" * 60)

    test_baudot_encoding()
    test_fsk_modulation()
    test_wav_roundtrip()
    test_full_message_encode_decode()

    print("\n" + "=" * 60)
    print("Tests complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
