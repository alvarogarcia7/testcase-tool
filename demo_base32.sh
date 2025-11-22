#!/bin/bash
# Demo: Base32 encoding (RECOMMENDED)

echo "=== BASE32 SOLUTION (Recommended) ==="
echo ""

# Encode
echo "1. Encoding files_1.zip..."
base32 files_1.zip > files_1_base32.txt

# Show stats
ORIG_SIZE=$(stat -c "%s" files_1.zip)
TEXT_SIZE=$(stat -c "%s" files_1_base32.txt)
OVERHEAD=$(python3 -c "print(f'{($TEXT_SIZE - $ORIG_SIZE) * 100 / $ORIG_SIZE:.1f}')")

echo "   Original size: $ORIG_SIZE bytes"
echo "   Encoded size:  $TEXT_SIZE bytes"
echo "   Overhead:      ${OVERHEAD}%"
echo ""

# Show sample
echo "2. First 200 characters to type:"
echo "   ----------------------------------------"
head -c 200 files_1_base32.txt
echo ""
echo "   ----------------------------------------"
echo ""

# Show line count
LINES=$(wc -l < files_1_base32.txt)
echo "3. Total lines to type: $LINES"
echo ""

# Test decode
echo "4. Testing decode..."
base32 -d files_1_base32.txt > files_1_reconstructed.zip

if cmp -s files_1.zip files_1_reconstructed.zip; then
    echo "   ✓ SUCCESS: Reconstructed file matches original!"
else
    echo "   ✗ FAILURE: Files don't match"
fi
echo ""

# Cleanup
rm -f files_1_reconstructed.zip

echo "=== DECODE COMMAND (one-liner for target computer) ==="
echo "base32 -d < file.txt > file.zip"
echo ""
