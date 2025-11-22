#!/bin/bash
# Quick script to encode a zip file for paper transfer (Base32 method)

if [ $# -eq 0 ]; then
    echo "Usage: $0 <zipfile>"
    echo ""
    echo "Encodes a ZIP file for printing and manual reconstruction."
    echo "Uses Base32 encoding (uppercase, no ambiguous characters)."
    echo ""
    echo "Example:"
    echo "  $0 myfile.zip > output.txt"
    echo "  $0 myfile.zip | lp    # Send directly to printer"
    exit 1
fi

ZIPFILE="$1"

if [ ! -f "$ZIPFILE" ]; then
    echo "Error: File '$ZIPFILE' not found" >&2
    exit 1
fi

# Print header
cat << EOF
========================================================================
ZIP FILE FOR PAPER TRANSFER
========================================================================
Original file: $ZIPFILE
File size: $(stat -c %s "$ZIPFILE") bytes
Encoded: $(date)
Encoding: Base32

TO RECONSTRUCT ON TARGET COMPUTER:
1. Type or paste the encoded text below into a file (e.g., file.txt)
2. Run: base32 -d < file.txt > output.zip
3. Verify: unzip -t output.zip

VERIFICATION CHECKSUM:
SHA256: $(sha256sum "$ZIPFILE" | cut -d' ' -f1)

========================================================================
ENCODED DATA (start typing below this line):
========================================================================

EOF

# Encode the file
base32 "$ZIPFILE"

# Print footer
cat << EOF

========================================================================
END OF DATA
========================================================================
After reconstructing, verify the SHA256 checksum matches.
EOF
