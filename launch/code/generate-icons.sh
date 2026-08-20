#!/usr/bin/env bash
# generate-icons.sh — generate all app icon sizes from master SVG
#
# Requires: rsvg-convert (librsvg2-bin) or inkscape or ImageMagick
#
# Output: launch/assets/icons/
#
# License: MIT

set -euo pipefail

SOURCE="${1:-launch/02_APP_ICON_SVG.svg}"
OUT_DIR="${2:-launch/assets/icons}"

if [[ ! -f "$SOURCE" ]]; then
  echo "❌ Source not found: $SOURCE"
  echo "Expected: launch/02_APP_ICON_SVG.svg"
  exit 1
fi

mkdir -p "$OUT_DIR"

# Choose converter
CONVERTER=""
if command -v rsvg-convert >/dev/null 2>&1; then
  CONVERTER="rsvg-convert"
elif command -v inkscape >/dev/null 2>&1; then
  CONVERTER="inkscape"
elif command -v convert >/dev/null 2>&1; then
  CONVERTER="convert"
else
  echo "❌ No SVG converter found. Install librsvg2-bin, inkscape, or ImageMagick"
  exit 1
fi

echo "🎨 Generating icons using $CONVERTER..."
echo "  Source: $SOURCE"
echo "  Output: $OUT_DIR"
echo ""

convert_svg() {
  local size="$1"
  local outfile="$2"
  case "$CONVERTER" in
    rsvg-convert)
      rsvg-convert -w "$size" -h "$size" "$SOURCE" -o "$outfile"
      ;;
    inkscape)
      inkscape "$SOURCE" --export-png="$outfile" -w "$size" -h "$size" 2>/dev/null
      ;;
    convert)
      convert -background none -density "$((size * 90 / 72))" "$SOURCE" -resize "${size}x${size}" "$outfile"
      ;;
  esac
}

# PNG sizes
for size in 16 32 48 64 128 256 512 1024; do
  echo "  icon-${size}.png"
  convert_svg "$size" "$OUT_DIR/icon-${size}.png"
done

# macOS .icns (multi-res)
if command -v iconutil >/dev/null 2>&1; then
  echo "  icon.icns (macOS)"
  ICONSET="$OUT_DIR/icon.iconset"
  mkdir -p "$ICONSET"
  cp "$OUT_DIR/icon-16.png" "$ICONSET/icon_16x16.png"
  cp "$OUT_DIR/icon-32.png" "$ICONSET/icon_16x16@2x.png"
  cp "$OUT_DIR/icon-32.png" "$ICONSET/icon_32x32.png"
  cp "$OUT_DIR/icon-64.png" "$ICONSET/icon_32x32@2x.png"
  cp "$OUT_DIR/icon-128.png" "$ICONSET/icon_128x128.png"
  cp "$OUT_DIR/icon-256.png" "$ICONSET/icon_128x128@2x.png"
  cp "$OUT_DIR/icon-256.png" "$ICONSET/icon_256x256.png"
  cp "$OUT_DIR/icon-512.png" "$ICONSET/icon_256x256@2x.png"
  cp "$OUT_DIR/icon-512.png" "$ICONSET/icon_512x512.png"
  cp "$OUT_DIR/icon-1024.png" "$ICONSET/icon_512x512@2x.png"
  iconutil -c icns "$ICONSET" -o "$OUT_DIR/icon.icns"
  rm -rf "$ICONSET"
elif command -v png2icns >/dev/null 2>&1; then
  echo "  icon.icns (macOS via png2icns)"
  png2icns "$OUT_DIR/icon.icns" \
    "$OUT_DIR/icon-16.png" "$OUT_DIR/icon-32.png" "$OUT_DIR/icon-64.png" \
    "$OUT_DIR/icon-128.png" "$OUT_DIR/icon-256.png" "$OUT_DIR/icon-512.png" \
    "$OUT_DIR/icon-1024.png"
fi

# Windows .ico
if command -v convert >/dev/null 2>&1; then
  echo "  icon.ico (Windows)"
  convert "$OUT_DIR/icon-256.png" \
    -define icon:auto-resize=16,32,48,64,128,256 \
    "$OUT_DIR/icon.ico"
fi

echo ""
echo "✅ Generated icons in $OUT_DIR"
ls -lh "$OUT_DIR"
