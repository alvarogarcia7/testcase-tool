#!/bin/bash
# Demo: Line checksums for error detection

echo "========================================================================="
echo "              LINE CHECKSUM DEMONSTRATION"
echo "========================================================================="
echo ""

# Create test data
echo "1. Creating test data with checksums..."
base32 files_1.zip | head -10 | ./add_line_checksums.sh - > demo_checksums.txt

echo "   First 3 lines with checksums:"
echo "   ----------------------------------------"
head -3 demo_checksums.txt | sed 's/^/   /'
echo "   ----------------------------------------"
echo "   Format: <data> <2-digit-hex-checksum>"
echo ""

# Calculate overhead
LINES=$(wc -l < demo_checksums.txt)
WITH_CS=$(cat demo_checksums.txt | wc -c)
WITHOUT_CS=$(base32 files_1.zip | head -10 | wc -c)
OVERHEAD=$((WITH_CS - WITHOUT_CS))

echo "2. Overhead analysis:"
echo "   Lines: $LINES"
echo "   Without checksums: $WITHOUT_CS bytes"
echo "   With checksums: $WITH_CS bytes"
echo "   Overhead: $OVERHEAD bytes ($(python3 -c "print(f'{$OVERHEAD * 100 / $WITHOUT_CS:.1f}')") %)"
echo "   Per line: $((OVERHEAD / LINES)) bytes"
echo ""

# Test correct verification
echo "3. Testing verification with CORRECT data..."
./verify_line_checksums.sh demo_checksums.txt demo_clean.txt 2>&1
echo ""

# Test error detection
echo "4. Testing error detection with CORRUPTED data..."
echo "   Corrupting line 5 (changing one character)..."
sed '5s/A/X/' demo_checksums.txt > demo_corrupted.txt

./verify_line_checksums.sh demo_corrupted.txt demo_clean2.txt 2>&1
EXIT_CODE=$?
echo ""

if [ $EXIT_CODE -ne 0 ]; then
    echo "   ✓ Error correctly detected and reported!"
else
    echo "   ✗ Error not detected (this shouldn't happen)"
fi
echo ""

# Show the power of line-by-line checking
echo "5. Incremental verification demo:"
echo "   Simulating typing first 5 lines..."
head -5 demo_checksums.txt > demo_partial.txt
echo "   Verifying first 5 lines..."
./verify_line_checksums.sh demo_partial.txt /dev/null 2>&1
echo ""
echo "   This allows you to verify as you type!"
echo ""

# Cleanup
rm -f demo_*.txt

echo "========================================================================="
echo "                         SUMMARY"
echo "========================================================================="
echo ""
echo "Line checksums provide:"
echo "  ✓ Immediate error detection (per line, not at the end)"
echo "  ✓ Precise error location (tells you exactly which line)"
echo "  ✓ Only ~4% size overhead (3 bytes per line)"
echo "  ✓ Peace of mind while typing"
echo ""
echo "Use: ./encode_with_line_checks.sh <file.zip> base32 > output.txt"
echo "========================================================================="
