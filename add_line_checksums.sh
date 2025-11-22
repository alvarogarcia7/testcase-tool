#!/bin/bash
# Add checksums to each line of an encoded file
# This allows line-by-line verification on the target computer

if [ $# -lt 1 ]; then
    echo "Usage: $0 <input_file> [output_file]"
    echo ""
    echo "Adds a checksum to the end of each line for verification."
    echo "The checksum is a 2-digit hex value (sum of bytes mod 256)."
    echo ""
    echo "Example:"
    echo "  base32 file.zip | $0 - > file_with_checksums.txt"
    echo "  $0 encoded.txt encoded_with_checksums.txt"
    exit 1
fi

INPUT="$1"
OUTPUT="${2:--}"  # default to stdout

# Create temp Python script
TMPSCRIPT=$(mktemp /tmp/add_checksums_XXXXXX.py)
trap "rm -f $TMPSCRIPT" EXIT

cat > "$TMPSCRIPT" << 'PYSCRIPT'
import sys

def compute_checksum(line):
    """Compute simple checksum: sum of all bytes modulo 256"""
    return sum(ord(c) for c in line.rstrip('\n')) % 256

# Read from file or stdin
input_file = sys.argv[1] if len(sys.argv) > 1 else '-'
output_file = sys.argv[2] if len(sys.argv) > 2 else '-'

if input_file == '-':
    lines = sys.stdin.readlines()
else:
    with open(input_file, 'r') as f:
        lines = f.readlines()

# Process each line
output_lines = []
for line in lines:
    line = line.rstrip('\n')
    if line.strip():  # only process non-empty lines
        checksum = compute_checksum(line)
        output_lines.append(f"{line} {checksum:02X}\n")
    else:
        output_lines.append("\n")

# Write to file or stdout
if output_file == '-':
    for line in output_lines:
        sys.stdout.write(line)
else:
    with open(output_file, 'w') as f:
        f.writelines(output_lines)
PYSCRIPT

# Execute Python script
python3 "$TMPSCRIPT" "$INPUT" "$OUTPUT"
