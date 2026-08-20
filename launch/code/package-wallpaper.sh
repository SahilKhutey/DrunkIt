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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

RELEASE_DIR="build/release/$VERSION"
WORK_DIR="$RELEASE_DIR/wallpaper"
mkdir -p "$WORK_DIR"

echo "🎨 Packaging Wallpaper Engine Workshop bundle..."

# Copy wallpaper build
if [[ -d "dist-wallpaper" ]]; then
  cp -r dist-wallpaper/* "$WORK_DIR/"
elif [[ -d "dist" ]]; then
  cp -r dist/* "$WORK_DIR/"
else
  echo "❌ Neither dist-wallpaper nor dist found. Run: npm run build:wallpaper"
  exit 1
fi

# Copy project.json and preview.png if available
if [[ -f "packaging/wallpaper-engine/project.json" ]]; then
  cp "packaging/wallpaper-engine/project.json" "$WORK_DIR/"
fi

if [[ -f "packaging/wallpaper-engine/preview.png" ]]; then
  cp "packaging/wallpaper-engine/preview.png" "$WORK_DIR/"
elif [[ -f "launch/assets/screenshots/workshop-thumbnail.png" ]]; then
  cp "launch/assets/screenshots/workshop-thumbnail.png" "$WORK_DIR/preview.png"
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
- Open source: github.com/SahilKhutey/Primodilas

License: MIT
EOF

# Create ZIP archive
ZIP_OUT="$RELEASE_DIR/primordials-wallpaper-$VERSION.zip"
if command -v zip >/dev/null 2>&1; then
  (cd "$WORK_DIR" && zip -r "../../primordials-wallpaper-$VERSION.zip" . -q)
  cp "$ZIP_OUT" "$WORK_DIR/primordials-wallpaper-$VERSION.zip" 2>/dev/null || true
else
  python -c "
import zipfile, os
work_dir = r'$WORK_DIR'
zip_out = r'$ZIP_OUT'
with zipfile.ZipFile(zip_out, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(work_dir):
        for f in files:
            fp = os.path.join(root, f)
            arcname = os.path.relpath(fp, work_dir)
            zf.write(fp, arcname)
print(f'Created {zip_out}')
"
fi

echo "✅ Wallpaper package: build/release/$VERSION/primordials-wallpaper-$VERSION.zip"
