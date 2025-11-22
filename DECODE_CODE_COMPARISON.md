# Decode Code Comparison
## How much code do you need to type on the target computer?

This is critical since you want to minimize typing on the second computer!

---

## Base32 (WINNER) - 1 line, 33 characters

```bash
base32 -d < file.txt > file.zip
```

**To type on target computer:**
1. Type the encoded data into `file.txt`
2. Type the one-line command above
3. Done!

**Total characters to type (besides data): 33**

---

## Base64 - 1 line, 33 characters

```bash
base64 -d < file.txt > file.zip
```

**To type on target computer:**
1. Type the encoded data into `file.txt`
2. Type the one-line command above
3. Done!

**Total characters to type (besides data): 33**

**BUT**: Much higher chance of typing errors in the data due to case sensitivity!

---

## Hexadecimal - 3 lines, 115 characters

```python
python3 << 'EOF'
data=open('f.txt').read().replace('\n','').strip()
open('f.zip','wb').write(bytes.fromhex(data))
EOF
```

Minimized version (97 chars):
```python
python3 -c "d=open('f.txt').read().replace('\n','');open('f.zip','wb').write(bytes.fromhex(d))"
```

**To type on target computer:**
1. Type the encoded data into `f.txt`
2. Type the 97-character Python one-liner
3. Done!

**Total characters to type (besides data): 97**

---

## Decimal - 5 lines, 134 characters

```python
python3 << 'EOF'
n=[]
for line in open('f.txt'):n.extend(int(x)for x in line.split())
open('f.zip','wb').write(bytes(n))
EOF
```

Minimized version (100 chars):
```python
python3 -c "n=[];[n.extend(int(x)for x in l.split())for l in open('f.txt')];open('f.zip','wb').write(bytes(n))"
```

**To type on target computer:**
1. Type the encoded data into `f.txt`
2. Type the 100-character Python one-liner
3. Done!

**Total characters to type (besides data): 100**

---

## Summary: Code Complexity on Target Computer

| Method | Lines | Characters | Complexity | Error Risk |
|--------|-------|------------|------------|------------|
| **Base32** | 1 | 33 | Very Low | Very Low |
| Base64 | 1 | 33 | Very Low | High (data errors) |
| Hexadecimal | 1 | 97 | Low | Low |
| Decimal | 1 | 100 | Low | Very Low |

---

## The Clear Winner: Base32

Base32 wins because:

1. **Shortest decode command** (33 chars, tied with Base64)
2. **No case sensitivity** in the data (Base64's Achilles heel)
3. **No ambiguous characters** in the data
4. **Reasonable file size** (62% overhead vs 300% for decimal)

You type:
- ~100 lines of clean uppercase + digits (for a 5KB file)
- 33 characters for the decode command
- Total: minimal, safe, simple

---

## Why Not Base64?

Base64 has the same simple decode command, BUT:

```
Data comparison for "testcase_template.yml":

Base64: UEsDBBQAAAAIADpNdVup5MhJ...
        ↑↑       ↑↑↑↑  ↑↑  ↑
        Case matters! O vs 0? I vs l vs 1?

Base32: KBFQGBAUAAAAACAAHJGXKW5J...
        ↑↑↑↑↑↑↑↑
        All uppercase, no confusion!
```

One typo in Base64 (O instead of 0, I instead of l) = corrupted file.
Base32 has no such ambiguity.

---

## Recommendation

**Use Base32:**
- Simplest decode (1 line, 33 chars)
- Safest data format
- Best overall balance

**The full command you type on the target computer:**
```bash
nano file.txt
# (type the base32 data from the printout)
# (Ctrl+X to save)
base32 -d < file.txt > file.zip
```

That's it!
