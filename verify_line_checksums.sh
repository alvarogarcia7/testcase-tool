#!/bin/bash
# Verify and remove checksums from each line
# Reports any lines with incorrect checksums

if [ $# -lt 1 ]; then
    echo "Usage: $0 <input_file> [output_file]"
    echo ""
    echo "Verifies line checksums and removes them."
    echo "Reports any lines with checksum errors."
    echo ""
    echo "Example:"
    echo "  $0 typed_data.txt clean_data.txt"
    echo "  $0 typed_data.txt - | base32 -d > file.zip"
    exit 1
fi

INPUT="$1"
OUTPUT="${2:--}"  # default to stdout

# Create temp Python script
TMPSCRIPT=$(mktemp /tmp/verify_checksums_XXXXXX.py)
trap "rm -f $TMPSCRIPT" EXIT

cat > "$TMPSCRIPT" << 'PYSCRIPT'
import sys

def compute_checksum(line):
    """Compute simple checksum: sum of all bytes modulo 256"""
    return sum(ord(c) for c in line) % 256

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
errors = []
line_num = 0

for line in lines:
    line_num += 1
    line = line.rstrip('\n')

    if not line.strip():  # empty line
        output_lines.append("\n")
        continue

    # Extract checksum (last 2 hex chars after space)
    parts = line.rsplit(' ', 1)
    if len(parts) == 2:
        data, checksum_str = parts
        try:
            expected_checksum = int(checksum_str, 16)
            actual_checksum = compute_checksum(data)

            if expected_checksum == actual_checksum:
                output_lines.append(data + "\n")
            else:
                errors.append(f"Line {line_num}: checksum mismatch (expected {expected_checksum:02X}, got {actual_checksum:02X})")
                output_lines.append(data + "\n")  # still output the data
        except ValueError:
            errors.append(f"Line {line_num}: invalid checksum format '{checksum_str}'")
            output_lines.append(line + "\n")  # output as-is
    else:
        errors.append(f"Line {line_num}: no checksum found")
        output_lines.append(line + "\n")  # output as-is

# Report errors to stderr
if errors:
    print("=" * 70, file=sys.stderr)
    print("CHECKSUM ERRORS DETECTED:", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    for error in errors:
        print(f"  ✗ {error}", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(f"Total: {len(errors)} error(s) found", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    sys.exit(1)
else:
    print(f"✓ All {line_num} lines verified successfully", file=sys.stderr)

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
