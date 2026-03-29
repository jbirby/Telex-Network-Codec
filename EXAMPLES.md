# Telex Codec Examples

## Example 1: Basic Message Encoding

Encode a simple message to telex audio:

```bash
cd scripts
python3 telex_encode.py "HELLO WORLD" hello.wav
```

This creates `hello.wav` containing the message "HELLO WORLD" encoded in ITA2 Baudot at 50 baud with FSK modulation.

## Example 2: Add Answerback Code

Each telex machine has a unique answerback code. Specify one when encoding:

```bash
python3 telex_encode.py "IMPORTANT MESSAGE" msg.wav --answerback NYC
```

The answerback "NYC" will be included in the message formatting.

## Example 3: Simulated Connection Handshake

Include connection handshake tones (dial tone, answerback exchange, GA signal):

```bash
python3 telex_encode.py "URGENT STOP" call.wav --answerback TLX001 --with-handshake
```

This simulates a complete telex call:
1. Dial tone (350+440 Hz)
2. Called machine's answerback (TLX001)
3. Go Ahead (GA) signal
4. Message transmission

## Example 4: Decode Recorded Telex

Decode a telex WAV file back to text:

```bash
python3 telex_decode.py hello.wav
```

Output:
```
TLE TLE
HELLO WORLD
+++
```

## Example 5: Save Decoded Text to File

```bash
python3 telex_decode.py call.wav decoded.txt
```

## Example 6: Identify Answerback

Show the machine's answerback when decoding:

```bash
python3 telex_decode.py call.wav --show-answerback
```

Output:
```
Answerback: TLX001
[decoded message text follows]
```

## Example 7: Encode from Text File

Create a message file and encode it:

```bash
cat > message.txt << 'EOF'
PLEASE SEND LATEST SALES FIGURES
REFERENCE QUARTER FOUR
REGARDS
EOF

python3 telex_encode.py message.txt sales_inquiry.wav --answerback SALES
```

## Example 8: Batch Processing

Encode multiple messages:

```bash
for file in *.txt; do
    python3 telex_encode.py "$file" "${file%.txt}.wav" --answerback BATCH
done
```

## Example 9: Full Workflow

Complete encode-decode cycle:

```bash
# 1. Create original message
echo "THIS IS A TELEX TEST MESSAGE" > original.txt

# 2. Encode with handshake
python3 telex_encode.py original.txt message.wav \
    --answerback TEST \
    --with-handshake

# 3. Decode back
python3 telex_decode.py message.wav decoded.txt

# 4. Compare
echo "Original:"
cat original.txt
echo -e "\nDecoded:"
cat decoded.txt
```

## Example 10: Custom Sample Rate

Encode at a different sample rate (e.g., 16 kHz):

```bash
python3 telex_encode.py "MESSAGE" output.wav --sample-rate 16000
```

## Example 11: Telex Conventions

Format a message using telex conventions:

```bash
python3 telex_encode.py \
    "NEW YORK BRANCH REPORTS SALES UP 15 PERCENT STOP RECOMMEND EXPANSION" \
    report.wav \
    --answerback NYC \
    --with-handshake
```

## Example 12: Testing

Verify the codec with the roundtrip test:

```bash
python3 test_roundtrip.py
```

This tests:
- Baudot encoding/decoding
- FSK modulation/demodulation
- WAV file I/O
- Full message encode/decode

## Technical Details

### Audio Specifications
- Format: 16-bit mono WAV
- Sample rate: 8000 Hz (default, configurable)
- Duration: ~150ms per character at 50 baud
- FSK Tones: 1400 Hz (mark), 1800 Hz (space)

### Baudot Character Set
- 5-bit encoding (32 possible values)
- Two modes: LTRS (letters) and FIGS (figures/numbers)
- Special codes: WRU (Who aRe yoU?), BEL (bell), mode switches

### Message Structure
```
+++ROUTING_PREFIX      (optional)
TLX: SENDER            (answerback code)
ACTUAL MESSAGE TEXT    (uppercase)
+++                    (end marker)
```

## Troubleshooting

### Encoding produces no sound
- Check that NumPy is installed: `pip install numpy`
- Verify the message is not empty
- Try a simple test: `python3 telex_encode.py "TEST" test.wav`

### Decoded text is garbled
- This is normal with FSK demodulation of noisy audio
- The codec uses simple correlators; real implementations use Viterbi decoders
- Baudot character accuracy depends on signal quality

### Answerback not appearing
- Answerback is formatted into the message, check output text
- Use `--show-answerback` flag when decoding to identify extracted codes

### WAV file won't play
- Ensure output file has `.wav` extension
- Check that `telex_common.py` is in the same directory
- Try different sample rate if audio sounds wrong
