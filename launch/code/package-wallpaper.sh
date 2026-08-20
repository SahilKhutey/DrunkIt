#!/usr/bin/env bash
# package-wallpaper.sh — build Wallpaper Engine Workshop package
#
# Output: build/release/<version>/wallpaper/primordials-wallpaper-<version>.zip
#
# License: MIT

set -euo pipefail

VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
  echo "Usage: $0 <version>"
  exit 1
fi

WORK_DIR="build/release/$VERSION/wallpaper"
mkdir -p "$WORK_DIR"

echo "🎨 Packaging Wallpaper Engine Workshop bundle..."

# Copy wallpaper build
if [[ -d "dist-wallpaper" ]]; then
  cp -r dist-wallpaper/* "$WORK_DIR/"
else
  echo "❌ dist-wallpaper not found. Run: npm run build:wallpaper"
  exit 1
fi

# Copy README for Workshop item
cat > "$WORK_DIR/README.txt" << EOF
Polygonal Primordials — Wallpaper Engine Edition
Version: $VERSION

INSTALLATION
1. Subscribe on Steam Workshop
2. Wallpaper Engine auto-detects
3. Configure via WE pause menu

CONTROLS
- Pause via WE pause menu (right-click)
- Adjust quality in WallpaperDock
- Switch biomes via settings panel

NOTES
- Auto-pauses when desktop is hidden
- Saves world every 60 seconds
- Open source: github.com/SahilKhutey/Primodials

License: MIT
EOF

# Create ZIP
cd "$WORK_DIR"
zip -r "../primordials-wallpaper-$VERSION.zip" . -q
cd - > /dev/null

echo "✅ Wallpaper package: build/release/$VERSION/wallpaper/primordials-wallpaper-$VERSION.zip"
ls -lh "build/release/$VERSION/wallpaper/"
