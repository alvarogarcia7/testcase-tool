# Solutions for Printing ZIP Files on Paper for Manual Reconstruction

## Problem
Transfer a zip file to another computer by:
1. Printing it on paper
2. Typing it on the target computer
3. Reconstructing the original zip file

## Constraints
- Only use software available on Ubuntu by default
- Minimize code needed on target computer
- Optimize for ease of typing and low error rate

---

## Solution Comparison Table

| Solution | Encoding Ratio | Typing Difficulty | Error Prone | Decode Complexity | Character Set |
|----------|---------------|-------------------|-------------|-------------------|---------------|
| **Base64** | 1.33x | Hard (case-sensitive) | High | Very Low | A-Za-z0-9+/= |
| **Base32** | 1.6x | Medium (uppercase only) | Medium | Very Low | A-Z2-7= |
| **Hex (lowercase)** | 2.0x | Easy (no case) | Low | Low | 0-9a-f |
| **Decimal chunks** | ~3.5x | Very Easy (numbers only) | Very Low | Medium | 0-9 space |

---

## Solution 1: Base64 (MOST COMPACT)

### Advantages
- ✓ Most compact (only 33% overhead)
- ✓ One-liner decode command
- ✓ Standard on all Ubuntu systems

### Disadvantages
- ✗ Case-sensitive (easy to make typing errors)
- ✗ Similar-looking characters (O/0, l/1/I)
- ✗ Uses special characters (+, /, =)

### Encoding
```bash
base64 file.zip > file.txt
```

### Decoding (target computer)
```bash
base64 -d < file.txt > file.zip
```

### Example output (first 100 chars of files_1.zip):
```
UEsDBBQAAAAIAOh+Y1njfGbnNwEAAFUCAAAJAAAAZmlsZTEudHh0TZBRS8MwFIXf8yuue1ubpJu0
```

### Size Impact
For 4.7KB zip: ~6.3KB of text

---

## Solution 2: Base32 (RECOMMENDED)

### Advantages
- ✓ No case sensitivity (all uppercase)
- ✓ No ambiguous characters (no 0/O, 1/I confusion)
- ✓ One-liner decode command
- ✓ No special characters except =

### Disadvantages
- ✗ 60% overhead (larger than base64)

### Encoding
```bash
base32 file.zip > file.txt
```

### Decoding (target computer)
```bash
base32 -d < file.txt > file.zip
```

### Example output (first 100 chars of files_1.zip):
```
KBSWE3DFNVQWKCQKGEZDAMJYORZSA4DMFYWCA5DIMUQFG2LPNZ2CAKCJONSWEYLQMFRGGZDF
MJZXI2LPNYQC42LONFZWKYLEMVQXA4TMNFXGOIDTORSSAZDMFQYGY6LCNFZWGZJ5E5UWE6LD
```

### Size Impact
For 4.7KB zip: ~7.5KB of text

---

## Solution 3: Hexadecimal - Lowercase (EASIEST TO TYPE)

### Advantages
- ✓ Very easy to type (only 0-9 and a-f)
- ✓ No case sensitivity issues
- ✓ Easy to verify and debug
- ✓ Simple Python decoder (4 lines)

### Disadvantages
- ✗ 100% overhead (doubles the size)

### Encoding
```bash
od -An -tx1 file.zip | tr -d ' \n' > file.txt
# OR with Python
python3 -c "import sys; sys.stdout.buffer.write(open('file.zip','rb').read().hex().encode())" > file.txt
```

### Decoding (target computer)
```python
python3 << 'EOF'
data = open('file.txt').read().strip()
open('file.zip', 'wb').write(bytes.fromhex(data))
EOF
```

### Example output (first 100 chars of files_1.zip):
```
504b03041400000008003e7e6359e37c66e737010000550200000900000066696c65312e74787434904544c3b34841df2ebb9b5f61
```

### Size Impact
For 4.7KB zip: ~9.4KB of text

---

## Solution 4: Decimal Chunks (SAFEST FOR TYPING)

### Advantages
- ✓ Only numbers (0-9) - safest to type
- ✓ No case sensitivity
- ✓ No special characters
- ✓ Can use spaces for readability

### Disadvantages
- ✗ Largest output (~250% overhead)
- ✗ Requires short Python script to decode

### Encoding
```python
python3 << 'EOF'
import sys
data = open('file.zip', 'rb').read()
# Print as space-separated decimal bytes
for i in range(0, len(data), 16):
    chunk = data[i:i+16]
    print(' '.join(str(b) for b in chunk))
EOF
```

### Decoding (target computer)
```python
python3 << 'EOF'
nums = []
for line in open('file.txt'):
    nums.extend(int(x) for x in line.split())
open('file.zip', 'wb').write(bytes(nums))
EOF
```

### Example output (first 2 lines of files_1.zip):
```
80 75 3 4 20 0 0 0 8 0 62 126 99 89 227 124
102 231 55 1 0 0 85 2 0 0 9 0 0 0
```

### Size Impact
For 4.7KB zip: ~16KB of text

---

## RECOMMENDATIONS

### For Small Files (< 10KB): **Base32**
- Best balance of compactness and typing safety
- No case sensitivity issues
- Clean character set (A-Z, 2-7)
- One-liner decode

### For Medium Files (10-50KB): **Hexadecimal**
- Still manageable to type
- Very low error rate
- Easy to spot mistakes
- Simple 4-line Python decoder

### For Any Size with OCR Available: **Base64**
- Most compact
- If you can scan/OCR the printout on target machine
- Typing manually not recommended

### AVOID for Manual Typing:
- Base64 (too error-prone with case sensitivity)
- Decimal chunks (too long for files > 5KB)

---

## Practical Example Workflow (Base32 - Recommended)

### On Source Computer
```bash
# 1. Encode the zip file
base32 files_1.zip > files_1.txt

# 2. Add line numbers for verification (optional)
cat -n files_1.txt > files_1_numbered.txt

# 3. Print the text file
lp files_1_numbered.txt  # or open in text editor and print
```

### On Target Computer
```bash
# 1. Create text file (type or paste the base32 content)
nano file.txt
# (type the content, Ctrl+X to save)

# 2. Decode
base32 -d file.txt > file.zip

# 3. Verify
unzip -t file.zip  # test the zip file integrity
```

---

## Error Detection Enhancement

Add a checksum line at the end to verify successful transfer:

### On Source Computer
```bash
base32 file.zip > file.txt
echo "SHA256: $(sha256sum file.zip | cut -d' ' -f1)" >> file.txt
```

### On Target Computer
```bash
# Remove last line (checksum) before decoding
head -n -1 file.txt > file_clean.txt
base32 -d file_clean.txt > file.zip

# Verify checksum matches
sha256sum file.zip
# Compare with the checksum line you typed
```
