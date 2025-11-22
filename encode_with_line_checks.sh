#!/bin/bash
# Encode a ZIP file with per-line checksums for paper transfer
# This version adds checksums to each line for better error detection

if [ $# -eq 0 ]; then
    echo "Usage: $0 <zipfile> [encoding]"
    echo ""
    echo "Encodes a ZIP file with line-by-line checksums for verification."
    echo "Each line has a 2-digit hex checksum appended."
    echo ""
    echo "Encoding options:"
    echo "  base32  - Base32 (default, recommended)"
    echo "  base64  - Base64 (most compact)"
    echo "  hex     - Hexadecimal"
    echo ""
    echo "Example:"
    echo "  $0 myfile.zip base32 > output.txt"
    echo "  $0 myfile.zip | lp    # print with default base32"
    exit 1
fi

ZIPFILE="$1"
ENCODING="${2:-base32}"

if [ ! -f "$ZIPFILE" ]; then
    echo "Error: File '$ZIPFILE' not found" >&2
    exit 1
fi

# Print header
cat << EOF
========================================================================
ZIP FILE FOR PAPER TRANSFER (WITH LINE CHECKSUMS)
========================================================================
Original file: $ZIPFILE
File size: $(stat -c %s "$ZIPFILE") bytes
Encoded: $(date)
Encoding: $ENCODING with line checksums

EACH LINE HAS A CHECKSUM:
Format: <data> <2-digit-hex-checksum>
Example: KBFQGBAUAAAAACAAHJGXKW5J4TEESKIFAAAA6DIAAAKQ 8F

TO RECONSTRUCT ON TARGET COMPUTER:
1. Type the encoded text below into a file (e.g., file.txt)
2. Verify checksums: ./verify_line_checksums.sh file.txt clean.txt
3. Decode: ${ENCODING} -d < clean.txt > output.zip
   (or use the all-in-one decoder script)
4. Verify: unzip -t output.zip

VERIFICATION CHECKSUM (overall file):
SHA256: $(sha256sum "$ZIPFILE" | cut -d' ' -f1)

========================================================================
ENCODED DATA (start typing below this line):
========================================================================

EOF

# Encode and add checksums
case "$ENCODING" in
    base32)
        base32 "$ZIPFILE" | ./add_line_checksums.sh -
        ;;
    base64)
        base64 "$ZIPFILE" | ./add_line_checksums.sh -
        ;;
    hex)
        python3 << PYEOF | ./add_line_checksums.sh -
data = open('$ZIPFILE', 'rb').read()
hex_str = data.hex()
for i in range(0, len(hex_str), 80):
    print(hex_str[i:i+80])
PYEOF
        ;;
    *)
        echo "Error: Unknown encoding '$ENCODING'" >&2
        exit 1
        ;;
esac

# Print footer
cat << EOF

========================================================================
END OF DATA
========================================================================

VERIFICATION INSTRUCTIONS:
1. After typing, verify line checksums to catch typing errors:
   ./verify_line_checksums.sh typed.txt clean.txt

2. If verification passes, decode:
   ${ENCODING} -d < clean.txt > file.zip

3. Verify final file matches:
   sha256sum file.zip
   (should match the SHA256 shown above)

The checksum at the end of each line helps catch typing errors
immediately, so you can fix them before trying to decode.
EOF
