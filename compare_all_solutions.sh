#!/bin/bash
# Compare all solutions side-by-side

echo "======================================================================="
echo "     ZIP FILE PAPER TRANSFER - SOLUTION COMPARISON"
echo "======================================================================="
echo ""
echo "Test file: files_1.zip ($(stat -c %s files_1.zip) bytes)"
echo ""

# Generate all encodings
base64 files_1.zip > /tmp/test_base64.txt
base32 files_1.zip > /tmp/test_base32.txt
python3 << 'EOF' > /tmp/test_hex.txt
data = open('files_1.zip', 'rb').read()
hex_str = data.hex()
for i in range(0, len(hex_str), 80):
    print(hex_str[i:i+80])
EOF

python3 << 'EOF' > /tmp/test_decimal.txt
data = open('files_1.zip', 'rb').read()
for i in range(0, len(data), 16):
    chunk = data[i:i+16]
    print(' '.join(f'{b:3d}' for b in chunk))
EOF

# Calculate stats
ORIG=$(stat -c %s files_1.zip)
BASE64_SIZE=$(stat -c %s /tmp/test_base64.txt)
BASE32_SIZE=$(stat -c %s /tmp/test_base32.txt)
HEX_SIZE=$(stat -c %s /tmp/test_hex.txt)
DEC_SIZE=$(stat -c %s /tmp/test_decimal.txt)

BASE64_LINES=$(wc -l < /tmp/test_base64.txt)
BASE32_LINES=$(wc -l < /tmp/test_base32.txt)
HEX_LINES=$(wc -l < /tmp/test_hex.txt)
DEC_LINES=$(wc -l < /tmp/test_decimal.txt)

printf "%-15s %10s %10s %8s %12s %s\n" "METHOD" "SIZE" "OVERHEAD" "LINES" "DECODE" "CHAR SET"
echo "-----------------------------------------------------------------------"
printf "%-15s %10s %9.1f%% %8s %12s %s\n" "Base64" "$BASE64_SIZE" "$(python3 -c "print((${BASE64_SIZE}-${ORIG})*100/${ORIG})")" "$BASE64_LINES" "1-liner" "A-Za-z0-9+/="
printf "%-15s %10s %9.1f%% %8s %12s %s\n" "Base32 ★" "$BASE32_SIZE" "$(python3 -c "print((${BASE32_SIZE}-${ORIG})*100/${ORIG})")" "$BASE32_LINES" "1-liner" "A-Z2-7="
printf "%-15s %10s %9.1f%% %8s %12s %s\n" "Hexadecimal" "$HEX_SIZE" "$(python3 -c "print((${HEX_SIZE}-${ORIG})*100/${ORIG})")" "$HEX_LINES" "4-line py" "0-9a-f"
printf "%-15s %10s %9.1f%% %8s %12s %s\n" "Decimal" "$DEC_SIZE" "$(python3 -c "print((${DEC_SIZE}-${ORIG})*100/${ORIG})")" "$DEC_LINES" "5-line py" "0-9 space"
echo ""
echo "★ = Recommended for manual typing"
echo ""

# Show typing difficulty assessment
echo "TYPING DIFFICULTY ASSESSMENT:"
echo ""
echo "Base64:      HIGH - Case sensitive, ambiguous chars (O/0, l/I/1)"
echo "Base32:      LOW  - Uppercase only, no ambiguous chars"
echo "Hexadecimal: LOW  - Lowercase only, simple chars"
echo "Decimal:     VERY LOW - Numbers only, but 3x longer"
echo ""

# Show sample outputs
echo "SAMPLE OUTPUT (first 160 chars):"
echo ""
echo "Base64:"
head -c 160 /tmp/test_base64.txt
echo ""
echo ""
echo "Base32:"
head -c 160 /tmp/test_base32.txt
echo ""
echo ""
echo "Hexadecimal:"
head -c 160 /tmp/test_hex.txt
echo ""
echo ""
echo "Decimal (first 3 lines):"
head -n 3 /tmp/test_decimal.txt
echo ""
echo ""

echo "======================================================================="
echo "RECOMMENDATION: Use Base32 for best balance of size and accuracy"
echo "======================================================================="
