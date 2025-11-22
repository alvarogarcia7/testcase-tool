#!/bin/bash
# Demo: Hexadecimal encoding

echo "=== HEXADECIMAL SOLUTION ==="
echo ""

# Encode using Python (more reliable than od)
echo "1. Encoding files_1.zip..."
python3 << 'EOF' > files_1_hex.txt
data = open('files_1.zip', 'rb').read()
hex_str = data.hex()
# Add newlines every 80 chars for readability
for i in range(0, len(hex_str), 80):
    print(hex_str[i:i+80])
EOF

# Show stats
ORIG_SIZE=$(stat -c "%s" files_1.zip)
TEXT_SIZE=$(stat -c "%s" files_1_hex.txt)
OVERHEAD=$(python3 -c "print(f'{($TEXT_SIZE - $ORIG_SIZE) * 100 / $ORIG_SIZE:.1f}')")

echo "   Original size: $ORIG_SIZE bytes"
echo "   Encoded size:  $TEXT_SIZE bytes"
echo "   Overhead:      ${OVERHEAD}%"
echo ""

# Show sample
echo "2. First 200 characters to type:"
echo "   ----------------------------------------"
head -c 200 files_1_hex.txt
echo ""
echo "   ----------------------------------------"
echo ""

# Show line count
LINES=$(wc -l < files_1_hex.txt)
echo "3. Total lines to type: $LINES"
echo ""

# Test decode
echo "4. Testing decode..."
python3 << 'EOF'
data = open('files_1_hex.txt').read().replace('\n', '').strip()
open('files_1_reconstructed.zip', 'wb').write(bytes.fromhex(data))
EOF

if cmp -s files_1.zip files_1_reconstructed.zip; then
    echo "   ✓ SUCCESS: Reconstructed file matches original!"
else
    echo "   ✗ FAILURE: Files don't match"
fi
echo ""

# Cleanup
rm -f files_1_reconstructed.zip

echo "=== DECODE COMMAND (for target computer) ==="
cat << 'EOF'
python3 << 'END'
data = open('file.txt').read().replace('\n', '').strip()
open('file.zip', 'wb').write(bytes.fromhex(data))
END
EOF
echo ""
