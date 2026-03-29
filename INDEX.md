# Telex Codec - Complete Project Index

## Quick Navigation

### Getting Started
- **QUICKSTART.md** - Start here! Installation and first usage
- **EXAMPLES.md** - Detailed usage examples and scenarios
- **README.md** - Comprehensive technical documentation

### Reference
- **MANIFEST.md** - Project overview and file listing
- **VERIFICATION.md** - Feature checklist and test results
- **SKILL.md** - Claude Code skill metadata

### Source Code
- **scripts/telex_common.py** - Core Baudot/FSK engine (~580 lines)
- **scripts/telex_encode.py** - CLI encoder (~120 lines)
- **scripts/telex_decode.py** - CLI decoder (~100 lines)
- **scripts/test_roundtrip.py** - Test suite (~180 lines)

### Legal
- **LICENSE** - MIT License

---

## What This Project Does

Encodes text messages into Telex network audio (WAV files) and decodes them back.

### Encoding Example
```bash
python3 scripts/telex_encode.py "HELLO WORLD" message.wav
```
Creates a WAV file containing the message encoded in ITA2 Baudot at 50 baud with FSK modulation (1400/1800 Hz).

### Decoding Example
```bash
python3 scripts/telex_decode.py message.wav
```
Converts the audio back to text.

---

## Key Features

✓ ITA2 Baudot code (5-bit, 2 modes)
✓ 50 baud FSK modulation (ITU-T standard)
✓ Telex answerback codes (machine identification)
✓ Connection handshake simulation (dial tone, GA signal)
✓ WRU (Who aRe yoU?) signal support
✓ 16-bit mono WAV file I/O
✓ Comprehensive command-line tools
✓ Full test suite included

---

## File Purpose Summary

| File | Purpose | Read Time |
|------|---------|-----------|
| QUICKSTART.md | Start here - setup and basics | 5 min |
| EXAMPLES.md | 12+ practical examples | 10 min |
| README.md | Complete technical docs | 20 min |
| MANIFEST.md | Project overview | 10 min |
| VERIFICATION.md | Feature checklist | 10 min |
| telex_common.py | Core codec engine | 30 min |
| telex_encode.py | Text-to-audio encoder | 10 min |
| telex_decode.py | Audio-to-text decoder | 10 min |
| test_roundtrip.py | Automated tests | 10 min |

---

## Quick Start (60 seconds)

1. **Install**
   ```bash
   pip install numpy
   ```

2. **Encode a message**
   ```bash
   cd scripts
   python3 telex_encode.py "HELLO" test.wav
   ```

3. **Decode it back**
   ```bash
   python3 telex_decode.py test.wav
   ```

4. **Success!** You've sent a telex message.

---

## Historical Context

**Telex** (Teleprinter Exchange) was the global standard for business communications from the 1930s through the 2000s:
- Landline-based (unlike RTTY which is radio)
- 50 baud speed (ITU-T international standard)
- Each machine had a unique "answerback" code (like a phone number)
- Messages followed strict formatting conventions
- Fully phased out by 2013 when major carriers shut down

This codec simulates the Telex network's encoding, signaling, and message format.

---

## Directory Structure

```
telex/
├── README.md              # Full documentation
├── QUICKSTART.md          # Get started here
├── EXAMPLES.md            # Usage scenarios
├── MANIFEST.md            # Project manifest
├── VERIFICATION.md        # Feature verification
├── SKILL.md               # Claude Code metadata
├── LICENSE                # MIT License
├── INDEX.md               # This file
└── scripts/
    ├── telex_common.py    # Core engine (Baudot + FSK)
    ├── telex_encode.py    # Text-to-audio
    ├── telex_decode.py    # Audio-to-text
    └── test_roundtrip.py  # Test suite
```

---

## Main Commands

### Encode (Text to Audio)
```bash
python3 scripts/telex_encode.py <message_text_or_file> <output.wav> [OPTIONS]

Options:
  --answerback CODE         Machine ID (e.g., NYC, TLX001)
  --with-handshake          Include dial tone + handshake
  --sample-rate RATE        Audio sample rate (default 8000)
```

### Decode (Audio to Text)
```bash
python3 scripts/telex_decode.py <input.wav> [output.txt] [OPTIONS]

Options:
  --show-answerback         Show machine ID in output
```

### Test
```bash
python3 scripts/test_roundtrip.py
```

---

## Technology Stack

- **Language**: Python 3.7+
- **Core Lib**: NumPy (DSP operations)
- **Audio Format**: PCM WAV (16-bit mono)
- **Modulation**: FSK (Frequency Shift Keying)
- **Character Encoding**: ITA2 Baudot
- **Baud Rate**: 50 (ITU-T standard)
- **Frequencies**: 1400 Hz (mark), 1800 Hz (space)

---

## Telex vs RTTY

| Aspect | Telex | RTTY |
|--------|-------|------|
| Medium | Landline phone | Radio (HF/VHF) |
| Era | 1930s-2000s | 1950s-present |
| Speed | 50 baud fixed | Variable (45-100) |
| Signaling | Rich (answerback) | Basic |
| Network | Switched circuit | Broadcast |
| ID | Answerback code | Call sign |

---

## Learning Path

1. **First 5 minutes**: Read QUICKSTART.md
2. **Next 10 minutes**: Try basic examples in EXAMPLES.md
3. **Next 20 minutes**: Read README.md technical section
4. **Next 15 minutes**: Review telex_common.py code
5. **Next 10 minutes**: Explore advanced examples in EXAMPLES.md

---

## Troubleshooting

**Q: ImportError: No module named numpy**
```bash
pip install numpy
```

**Q: WAV file sounds wrong**
Try at 16kHz sample rate:
```bash
python3 scripts/telex_encode.py "TEST" out.wav --sample-rate 16000
```

**Q: Decoded text is garbled**
This is normal! Simple FSK demodulation is sensitive to noise. Real telex machines used phase-lock loops. See VERIFICATION.md for details.

**Q: How do I know the code works?**
Run the test suite:
```bash
python3 scripts/test_roundtrip.py
```

---

## Related Projects

- **RTTY Codec** - Radio teleprinter (45.45/50/75/100 baud)
- **FAX Codec** - Facsimile transmission (T.4/V.27ter)
- **SSTV Codec** - Slow-scan TV (amateur radio pictures)
- **APT Codec** - NOAA weather satellite pictures
- **Data Modem** - Generic FSK modem for binary files

---

## Documentation Files

### QUICKSTART.md (150 lines)
Fast setup and first usage guide. Start here!

### README.md (400 lines)
Full technical documentation including:
- Telex network history
- Technical specifications
- Command reference
- Implementation details
- Future enhancements

### EXAMPLES.md (250 lines)
Twelve detailed usage examples from simple to advanced, plus troubleshooting.

### MANIFEST.md (300 lines)
Complete project manifest listing all components, features, and statistics.

### VERIFICATION.md (180 lines)
Component checklist, test results, feature verification, and quality metrics.

### SKILL.md (8 lines)
Claude Code skill metadata for integration.

---

## Code Files

### telex_common.py (580 lines)
Core codec engine:
- ITA2 Baudot character tables and encoding
- FSK modulation and demodulation
- Telex network features (answerback, WRU, GA)
- Connection handshake simulation
- WAV file I/O

### telex_encode.py (120 lines)
CLI tool for encoding text to audio:
- Reads text or file input
- Formats as telex message
- Optional handshake simulation
- Outputs WAV file

### telex_decode.py (100 lines)
CLI tool for decoding audio to text:
- Reads WAV file
- Demodulates FSK
- Decodes Baudot
- Cleans up message format

### test_roundtrip.py (180 lines)
Comprehensive test suite:
- Baudot encoding/decoding tests
- FSK modulation tests
- WAV file I/O tests
- Full message roundtrip tests

---

## Project Statistics

- Total Files: 11
- Source Code: 980 lines
- Documentation: 1,180 lines
- Total Content: 2,160 lines
- Python: 3.7+
- Dependencies: NumPy only
- License: MIT
- Status: Complete and tested

---

## Next Steps

1. Read QUICKSTART.md (5 minutes)
2. Run `python3 scripts/test_roundtrip.py` (30 seconds)
3. Try `python3 scripts/telex_encode.py "TEST" test.wav` (10 seconds)
4. Explore EXAMPLES.md (10 minutes)
5. Read README.md for deep dive (20 minutes)

---

## Support

For issues or questions:
1. Check QUICKSTART.md troubleshooting section
2. Review EXAMPLES.md for similar usage
3. Check VERIFICATION.md for known limitations
4. Read README.md technical details

---

**Created**: March 2026
**License**: MIT
**Status**: Complete, tested, and documented

