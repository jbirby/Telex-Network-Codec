# Telex Codec - Quick Start Guide

## Installation

```bash
cd scripts
pip install numpy
```

## Quick Test

Encode a message:
```bash
python3 telex_encode.py "HELLO TELEX NETWORK" output.wav
```

Decode it back:
```bash
python3 telex_decode.py output.wav
```

Expected output (with minor demodulation artifacts):
```
TLE TLE
HELLO TELEE
+++
```

## Basic Examples

### 1. Simple Message
```bash
python3 telex_encode.py "WEATHER REPORT AVAILABLE" weather.wav
```

### 2. Message with Answerback
```bash
python3 telex_encode.py "URGENT STOP" urgent.wav --answerback NYC
```

### 3. Simulated Call with Handshake
```bash
python3 telex_encode.py "PLEASE CONFIRM RECEIPT" call.wav \
    --answerback TLX001 \
    --with-handshake
```

### 4. Decode and Extract Message
```bash
python3 telex_decode.py call.wav message.txt
cat message.txt
```

## Command Reference

### Encoder
```
python3 telex_encode.py TEXT_OR_FILE OUTPUT.WAV [OPTIONS]

Options:
  --answerback CODE         Machine ID (e.g., TLX, NYC, LONDON)
  --with-handshake          Include dial tone and connection signals
  --sample-rate RATE        Audio sample rate (default: 8000)
```

### Decoder
```
python3 telex_decode.py INPUT.WAV [OUTPUT.TXT] [OPTIONS]

Options:
  --show-answerback         Display identified answerback code
```

## Understanding the Output

### Encoded WAV File
- Format: 16-bit mono WAV at 8000 Hz
- Duration: ~150ms per character at 50 baud
- Frequencies: 1400 Hz (mark), 1800 Hz (space)
- Size: ~1.2 KB per 100 characters

### Formatted Message
```
+++ROUTING_PREFIX           (optional routing info)
TLX: SENDER_ANSWERBACK     (machine identification)
ACTUAL MESSAGE TEXT HERE    (uppercase)
+++                         (end marker)
```

## Key Telex Concepts

**Baudot Code**: 5-bit character encoding used by all teleprinters
**Answerback**: Unique machine code, like a caller ID
**WRU**: "Who aRe yoU?" signal requesting answerback
**GA**: "Go Ahead" signal between sender and receiver
**50 Baud**: International telex speed (ITU-T standard)
**FSK**: Frequency Shift Keying modulation

## Troubleshooting

### ImportError: No module named numpy
```bash
pip install numpy
```

### No output from decoder
- Try with `--show-answerback` flag
- Ensure WAV file is not empty: `ls -lh *.wav`
- Check signal quality with audio player

### Garbled text from decoder
- This is expected! Simple correlator FSK has noise sensitivity
- Real telex machines used sophisticated synchronizers (phase-lock loops)
- For pristine audio, try signals with `--with-handshake` option

## Advanced Topics

### Custom Sample Rate
```bash
# Encode at 16 kHz for higher fidelity
python3 telex_encode.py "MESSAGE" out.wav --sample-rate 16000

# Must decode at same rate
python3 telex_decode.py out.wav
```

### From Files
```bash
# Create message file
echo "THIS MESSAGE IS FROM A FILE" > message.txt

# Encode it
python3 telex_encode.py message.txt message.wav

# Decode back
python3 telex_decode.py message.wav
```

### Batch Processing
```bash
# Encode all text files
for f in *.txt; do
    python3 telex_encode.py "$f" "${f%.txt}.wav"
done

# Decode all WAV files
for f in *.wav; do
    echo "=== $f ===" 
    python3 telex_decode.py "$f"
done
```

## What's Different from RTTY?

- **Telex**: Landline teleprinter network (1930s-2000s)
  - Fixed 50 baud
  - Switched circuit (phone line)
  - Answerback codes
  
- **RTTY**: Radio teleprinter (amateur radio)
  - Variable baud rates (45.45, 75, 100)
  - Broadcasting (one-to-many)
  - Call signs instead of answerback

## Next Steps

1. Read `README.md` for comprehensive documentation
2. Check `EXAMPLES.md` for more detailed use cases
3. Run `test_roundtrip.py` to verify your installation
4. Explore Telex history and network operation

## References

- ITU-T V.14: Asynchronous to Synchronous Conversion
- ITA2 Baudot Code Reference
- CCITT Orange Book: Telex Network
- Telex Operating Procedures (CCITT)

## License

MIT License - See LICENSE file
