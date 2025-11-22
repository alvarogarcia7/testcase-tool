#!/bin/bash
# Demo: Decimal encoding (numbers only)

echo "=== DECIMAL SOLUTION (Numbers Only) ==="
echo ""

# Encode
echo "1. Encoding files_1.zip..."
python3 << 'EOF' > files_1_decimal.txt
data = open('files_1.zip', 'rb').read()
# Print as space-separated decimal bytes, 16 per line
for i in range(0, len(data), 16):
    chunk = data[i:i+16]
    print(' '.join(f'{b:3d}' for b in chunk))
EOF

# Show stats
ORIG_SIZE=$(stat -c "%s" files_1.zip)
TEXT_SIZE=$(stat -c "%s" files_1_decimal.txt)
OVERHEAD=$(python3 -c "print(f'{($TEXT_SIZE - $ORIG_SIZE) * 100 / $ORIG_SIZE:.1f}')")

echo "   Original size: $ORIG_SIZE bytes"
echo "   Encoded size:  $TEXT_SIZE bytes"
echo "   Overhead:      ${OVERHEAD}%"
echo ""

# Show sample
echo "2. First 5 lines to type:"
echo "   ----------------------------------------"
head -n 5 files_1_decimal.txt
echo "   ----------------------------------------"
echo ""

# Show line count
LINES=$(wc -l < files_1_decimal.txt)
echo "3. Total lines to type: $LINES"
echo ""

# Test decode
echo "4. Testing decode..."
python3 << 'EOF'
nums = []
for line in open('files_1_decimal.txt'):
    nums.extend(int(x) for x in line.split())
open('files_1_reconstructed.zip', 'wb').write(bytes(nums))
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
nums = []
for line in open('file.txt'):
    nums.extend(int(x) for x in line.split())
open('file.zip', 'wb').write(bytes(nums))
END
EOF
echo ""
