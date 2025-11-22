# ZIP File Paper Transfer Guide

## Problem Statement
Transfer a ZIP file to another computer by printing it on paper, typing it in manually, and reconstructing it - using only standard Ubuntu software.

## Quick Start (TL;DR)

**Recommended Method: Base32 Encoding**

### On Source Computer:
```bash
./encode_for_paper.sh myfile.zip > printable.txt
# Print printable.txt or just use:
./encode_for_paper.sh myfile.zip | lp
```

### On Target Computer:
```bash
# Type the encoded data into a file named typed.txt
# Then run:
base32 -d < typed.txt > myfile.zip
unzip -t myfile.zip  # verify integrity
```

---

## Solution Comparison

| Method | Size Overhead | Typing Difficulty | Decode Complexity | Best For |
|--------|--------------|-------------------|-------------------|----------|
| **Base32** ⭐ | +62% | Low | One-liner | **Recommended** |
| Base64 | +35% | High | One-liner | OCR scanning |
| Hexadecimal | +103% | Low | 4-line Python | Medium files |
| Decimal | +300% | Very Low | 5-line Python | Avoid (too long) |

### Why Base32 is Recommended:
- ✅ Uppercase only (no case sensitivity issues)
- ✅ No ambiguous characters (no O vs 0, or I vs 1 confusion)
- ✅ One-line decode command
- ✅ Compact enough for practical use
- ✅ Only uses: A-Z, 2-7, and = (no special chars to confuse)

---

## Detailed Solutions

### Solution 1: Base32 (RECOMMENDED) ⭐

**Encoding:**
```bash
base32 file.zip > file.txt
```

**Decoding:**
```bash
base32 -d < file.txt > file.zip
```

**Example Output:**
```
KBFQGBAUAAAAACAAHJGXKW5J4TEESKIFAAAA6DIAAAKQAAAAORSXG5DDMFZWKX3UMVWXA3DBORSS
46LNNS6VPW3O3M4BA7OXK4GJIBO2AK3CEOYXURBLCWFPTW3EULYJCKTS2FQBARNJVWG4JCSCUUSJ
```

**Pros:**
- Uppercase only - easy to type without case errors
- No confusing characters (uses A-Z and 2-7)
- One-liner decode command

**Cons:**
- 62% larger than original file

**File Size Impact (for 4.7KB zip):**
- Original: 4,733 bytes
- Encoded: 7,676 bytes
- Lines to type: ~100

---

### Solution 2: Base64 (Most Compact)

**Encoding:**
```bash
base64 file.zip > file.txt
```

**Decoding:**
```bash
base64 -d < file.txt > file.zip
```

**Example Output:**
```
UEsDBBQAAAAIADpNdVup5MhJKQUAAA8NAAAVAAAAdGVzdGNhc2VfdGVtcGxhdGUueW1svVfbbts4
EH3XVwyUBdoCtiI7F6RCsVivnbZKLwkSpy0WAQRamtjcSKQqUkncbv99h6TkyE7STV82L7ZJzu3M
```

**Pros:**
- Most compact (only 35% overhead)
- One-liner decode command
- Standard on all systems

**Cons:**
- ⚠️ CASE SENSITIVE - very error prone!
- Confusing characters: O vs 0, l vs I vs 1
- Special characters: + / =

**Not recommended for manual typing due to high error rate**

**File Size Impact (for 4.7KB zip):**
- Original: 4,733 bytes
- Encoded: 6,396 bytes
- Lines to type: ~84

---

### Solution 3: Hexadecimal (Easy to Type)

**Encoding:**
```bash
python3 << 'EOF' > file.txt
data = open('file.zip', 'rb').read()
hex_str = data.hex()
for i in range(0, len(hex_str), 80):
    print(hex_str[i:i+80])
EOF
```

**Decoding:**
```bash
python3 << 'EOF'
data = open('file.txt').read().replace('\n', '').strip()
open('file.zip', 'wb').write(bytes.fromhex(data))
EOF
```

**Example Output:**
```
504b03041400000008003a4d755ba9e4c849290500000f0d00001500000074657374636173655f74
656d706c6174652e796d6cbd57db6edb38107dd7570c9405da02b6223b17a442b158af9db64a2f09
```

**Pros:**
- Only lowercase hex (0-9, a-f)
- No case sensitivity
- Easy to spot errors
- Simple to verify

**Cons:**
- 103% overhead (doubles size)
- Requires 4-line Python script to decode

**File Size Impact (for 4.7KB zip):**
- Original: 4,733 bytes
- Encoded: 9,585 bytes
- Lines to type: ~119

---

### Solution 4: Decimal (Numbers Only)

**Encoding:**
```bash
python3 << 'EOF' > file.txt
data = open('file.zip', 'rb').read()
for i in range(0, len(data), 16):
    chunk = data[i:i+16]
    print(' '.join(f'{b:3d}' for b in chunk))
EOF
```

**Decoding:**
```bash
python3 << 'EOF'
nums = []
for line in open('file.txt'):
    nums.extend(int(x) for x in line.split())
open('file.zip', 'wb').write(bytes(nums))
EOF
```

**Example Output:**
```
 80  75   3   4  20   0   0   0   8   0  58  77 117  91 169 228
200  73  41   5   0   0  15  13   0   0  21   0   0   0 116 101
115 116  99  97 115 101  95 116 101 109 112 108  97 116 101  46
```

**Pros:**
- Only numbers (0-9) - safest character set
- No special characters
- Very low error rate

**Cons:**
- 300% overhead (4x larger!)
- Way too long for files > 2KB
- Requires 5-line Python script

**File Size Impact (for 4.7KB zip):**
- Original: 4,733 bytes
- Encoded: 18,932 bytes
- Lines to type: ~296

**Not recommended except for very small files**

---

## Verification and Error Detection

### Add Checksums

To verify successful transfer, include a checksum:

**On Source Computer:**
```bash
base32 file.zip > file.txt
echo "SHA256: $(sha256sum file.zip | cut -d' ' -f1)" >> file.txt
```

**On Target Computer:**
```bash
# Decode (remove last checksum line first)
head -n -1 file.txt | base32 -d > file.zip

# Verify
sha256sum file.zip
# Compare with the SHA256 line you typed
```

The provided `encode_for_paper.sh` script automatically includes checksums.

---

## Practical Example: Complete Workflow

### Step 1: On Source Computer

```bash
# Generate printable version
./encode_for_paper.sh mydata.zip > to_print.txt

# Print it
cat to_print.txt | lp
# or open in text editor and print from there
```

### Step 2: On Target Computer

```bash
# Create a new file and type the encoded data
nano typed_data.txt
# Type the base32 text from the printed page
# Save with Ctrl+X

# Decode using the helper script
./decode_from_paper.sh typed_data.txt mydata.zip

# Or manually:
base32 -d < typed_data.txt > mydata.zip

# Verify integrity
unzip -t mydata.zip
sha256sum mydata.zip  # Compare with printed checksum
```

---

## Size Guidelines

**Practical limits for manual typing:**

| File Size | Base32 Lines | Time Estimate | Recommendation |
|-----------|--------------|---------------|----------------|
| < 5 KB | ~100 lines | 15-30 min | ✅ Practical |
| 5-10 KB | ~200 lines | 30-60 min | ⚠️ Tedious but doable |
| 10-20 KB | ~400 lines | 1-2 hours | ⚠️ Very tedious |
| > 20 KB | > 400 lines | > 2 hours | ❌ Consider alternatives |

---

## Tips for Error-Free Typing

1. **Use Base32** - uppercase only, no ambiguous characters
2. **Type in chunks** - decode and verify every 50-100 lines
3. **Use line numbers** - helps track progress and find errors
4. **Double-check similar characters:**
   - In Base32: 2 vs Z, 5 vs S, 0 never appears (uses O instead? No, uses 2-7)
5. **Use monospace font** when printing
6. **Print checksums** to verify correctness
7. **Consider OCR** if you have a scanner on target machine

---

## Alternative Approaches (for comparison)

### QR Codes
- Could split into multiple QR codes
- Requires QR code generator/reader (not standard on Ubuntu)
- Practical for very small files only

### Audio/DTMF
- Encode as audio tones
- Requires audio recording capability
- Complex to implement

### OCR
- Print normally, scan on target
- Requires scanner on target machine
- If available, just use Base64 for maximum compactness

---

## Files Included

| File | Description |
|------|-------------|
| `encode_for_paper.sh` | Easy-to-use encoder with headers and checksums |
| `decode_from_paper.sh` | Easy-to-use decoder with verification |
| `compare_all_solutions.sh` | Side-by-side comparison of all methods |
| `demo_base32.sh` | Demonstration of Base32 method |
| `demo_hex.sh` | Demonstration of hexadecimal method |
| `demo_base64.sh` | Demonstration of Base64 method |
| `demo_decimal.sh` | Demonstration of decimal method |

---

## Conclusion

**For manual typing: Use Base32**
- Best balance of size and typing safety
- No confusing characters
- One-liner decode
- ~60% overhead is acceptable for small files

**Use the provided scripts for convenience:**
- `encode_for_paper.sh` - handles everything automatically
- `decode_from_paper.sh` - includes verification

**Maximum recommended file size: 10KB** (about 200 lines of typing)
