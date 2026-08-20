#!/usr/bin/env bash
# generate-icons.sh — generate all app icon sizes from master SVG
#
# Requires: Python (Pillow) or rsvg-convert
#
# Output: launch/assets/icons/
#
# License: MIT

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

SOURCE="${1:-$PROJECT_ROOT/launch/02_APP_ICON_SVG.svg}"
OUT_DIR="${2:-$PROJECT_ROOT/launch/assets/icons}"

if [[ ! -f "$SOURCE" ]]; then
  echo "❌ Source not found: $SOURCE"
  exit 1
fi

mkdir -p "$OUT_DIR"

echo "🎨 Generating icons..."
echo "  Source: $SOURCE"
echo "  Output: $OUT_DIR"

if command -v python >/dev/null 2>&1; then
  python "$SCRIPT_DIR/generate-icons.py" "$SOURCE" "$OUT_DIR"
elif command -v python3 >/dev/null 2>&1; then
  python3 "$SCRIPT_DIR/generate-icons.py" "$SOURCE" "$OUT_DIR"
elif command -v rsvg-convert >/dev/null 2>&1; then
  for size in 16 32 48 64 128 256 512 1024; do
    rsvg-convert -w "$size" -h "$size" "$SOURCE" -o "$OUT_DIR/icon-${size}.png"
  done
  cp "$OUT_DIR/icon-1024.png" "$OUT_DIR/icon-master-1024.png"
  cp "$SOURCE" "$OUT_DIR/icon-master-1024.svg"
fi

echo ""
echo "✅ Generated icons in $OUT_DIR"

