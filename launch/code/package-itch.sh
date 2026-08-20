#!/usr/bin/env bash
# package-itch.sh — build itch.io standalone ZIP
#
# Output: build/release/<version>/itch/primordials-itch-<version>.zip
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
WORK_DIR="$RELEASE_DIR/itch"
mkdir -p "$WORK_DIR/primordials"

echo "🎮 Packaging itch.io bundle..."

# Copy web build
if [[ -d "dist" ]]; then
  cp -r dist/* "$WORK_DIR/primordials/"
else
  echo "❌ dist not found. Run: npm run build"
  exit 1
fi

# Include sample biomes
if [[ -d "biomes" ]]; then
  cp -r biomes "$WORK_DIR/primordials/"
fi

# Add README
cat > "$WORK_DIR/primordials/README.txt" << EOF
Polygonal Primordials — itch.io Edition
Version: $VERSION

HOW TO RUN
1. Unzip this folder anywhere
2. Open index.html in any modern browser
3. Optional: append ?wallpaper=1 for wallpaper mode

FEATURES
- 6 biomes (algae bloom, deep sea, primordial soup, tundra, coral reef, volcanic vent)
- Real-time predator-prey simulation
- Pause, speed control, reset
- Local save/load
- Custom biome JSON support

LICENSE
MIT — see LICENSE file in the zip or visit github.com/SahilKhutey/Primodials

LINKS
Website: https://primordials.dev
GitHub: https://github.com/SahilKhutey/Primodials
Discord: https://discord.gg/primordials
EOF

# Create ZIP archive
ZIP_OUT="$RELEASE_DIR/primordials-itch-$VERSION.zip"
if command -v zip >/dev/null 2>&1; then
  (cd "$WORK_DIR" && zip -r "../../primordials-itch-$VERSION.zip" primordials -q)
  cp "$ZIP_OUT" "$WORK_DIR/primordials-itch-$VERSION.zip" 2>/dev/null || true
else
  python -c "
import zipfile, os
work_dir = r'$WORK_DIR'
zip_out = r'$ZIP_OUT'
with zipfile.ZipFile(zip_out, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(os.path.join(work_dir, 'primordials')):
        for f in files:
            fp = os.path.join(root, f)
            arcname = os.path.relpath(fp, work_dir)
            zf.write(fp, arcname)
print(f'Created {zip_out}')
"
fi

echo "✅ itch.io package: build/release/$VERSION/primordials-itch-$VERSION.zip"

