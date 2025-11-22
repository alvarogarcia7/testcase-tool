#!/bin/bash
# Quick script to decode a paper-transferred zip file

if [ $# -eq 0 ]; then
    echo "Usage: $0 <encoded_file.txt> [output.zip]"
    echo ""
    echo "Decodes a Base32-encoded ZIP file from paper transfer."
    echo ""
    echo "Example:"
    echo "  $0 typed_data.txt myfile.zip"
    echo "  $0 typed_data.txt    # outputs to decoded.zip"
    exit 1
fi

INPUT="$1"
OUTPUT="${2:-decoded.zip}"

if [ ! -f "$INPUT" ]; then
    echo "Error: Input file '$INPUT' not found" >&2
    exit 1
fi

echo "Decoding $INPUT..."
echo ""

# Extract only the base32 data (between the markers)
# Skip header and footer
sed -n '/^ENCODED DATA/,/^END OF DATA/p' "$INPUT" | \
    grep -v "^ENCODED DATA" | \
    grep -v "^END OF DATA" | \
    grep -v "^===" | \
    grep -v "^$" | \
    base32 -d > "$OUTPUT" 2>&1

if [ $? -eq 0 ]; then
    echo "✓ Decode successful!"
    echo "  Output: $OUTPUT"
    echo "  Size: $(stat -c %s "$OUTPUT") bytes"
    echo ""

    # Test if it's a valid zip
    if unzip -t "$OUTPUT" >/dev/null 2>&1; then
        echo "✓ ZIP file integrity check passed!"
    else
        echo "✗ WARNING: ZIP file may be corrupted!"
        echo "  Check for typing errors in the encoded data."
    fi

    echo ""
    echo "SHA256: $(sha256sum "$OUTPUT" | cut -d' ' -f1)"
    echo ""
    echo "Compare this checksum with the one in the header of $INPUT"
else
    echo "✗ Decode failed!"
    echo "  Check that the input file contains valid Base32 data."
    exit 1
fi
