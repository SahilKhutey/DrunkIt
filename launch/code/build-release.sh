#!/usr/bin/env bash
# build-release.sh — reproducible release for Polygonal Primordials
#
# Usage:
#   ./launch/code/build-release.sh <version>              # full release
#   ./launch/code/build-release.sh <version> --dry-run    # no artifacts written
#   ./launch/code/build-release.sh <version> --skip-tests # NOT recommended
#
# License: MIT

set -euo pipefail

VERSION="${1:-}"
DRY_RUN=false
SKIP_TESTS=false

# ─── Parse args ──────────────────────────────────────
shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)    DRY_RUN=true ;;
    --skip-tests) SKIP_TESTS=true ;;
    *) echo "Unknown flag: $1"; exit 1 ;;
  esac
  shift
done

# ─── Validate ────────────────────────────────────────
if [[ -z "$VERSION" ]]; then
  echo "Usage: $0 <version> [--dry-run] [--skip-tests]"
  exit 1
fi

if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Version must be semver (e.g., 1.0.0)"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "❌ Missing: $1"
    exit 1
  fi
}

require_command node
require_command npm
require_command git

echo "🧬 Polygonal Primordials release builder"
echo "📦 Version: $VERSION"
echo "🔍 Dry run: $DRY_RUN"
echo ""

# ─── Clean ───────────────────────────────────────────
echo "🧹 Cleaning..."
[[ "$DRY_RUN" = false ]] && rm -rf "build/release/$VERSION"

# ─── Install deps ────────────────────────────────────
echo "📦 Installing dependencies..."
if [[ "$DRY_RUN" = false ]]; then
  npm ci 2>/dev/null || npm install --prefer-offline
fi

# ─── Quality checks ──────────────────────────────────
echo "🔍 Type check..."
[[ "$DRY_RUN" = false ]] && npm run typecheck

echo "🔍 Lint..."
[[ "$DRY_RUN" = false ]] && npm run lint

if [[ "$SKIP_TESTS" = false ]]; then
  echo "🧪 Tests..."
  [[ "$DRY_RUN" = false ]] && npm run test
fi

# ─── Build web app ───────────────────────────────────
echo "🏗️ Building web app..."
if [[ "$DRY_RUN" = false ]]; then
  npm run build
fi

# ─── Build wallpaper package ────────────────────────
echo "🎨 Building wallpaper package..."
if [[ "$DRY_RUN" = false ]]; then
  npm run build:wallpaper
  bash "$SCRIPT_DIR/package-wallpaper.sh" "$VERSION"
fi

# ─── Build itch package ──────────────────────────────
echo "🎮 Building itch.io package..."
if [[ "$DRY_RUN" = false ]]; then
  bash "$SCRIPT_DIR/package-itch.sh" "$VERSION"
fi

# ─── Package standalone web ──────────────────────────
echo "🌐 Packaging standalone web app..."
if [[ "$DRY_RUN" = false ]]; then
  WEB_DIR="build/release/$VERSION/web"
  mkdir -p "$WEB_DIR"
  cp -r dist/* "$WEB_DIR/"
  
  ZIP_WEB="build/release/$VERSION/primordials-web-$VERSION.zip"
  if command -v zip >/dev/null 2>&1; then
    (cd "$WEB_DIR" && zip -r "../primordials-web-$VERSION.zip" . -q)
  else
    python -c "
import zipfile, os
work_dir = r'$WEB_DIR'
zip_out = r'$ZIP_WEB'
with zipfile.ZipFile(zip_out, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(work_dir):
        for f in files:
            fp = os.path.join(root, f)
            arcname = os.path.relpath(fp, work_dir)
            zf.write(fp, arcname)
print(f'Created {zip_out}')
"
  fi
fi

# ─── Generate checksums ──────────────────────────────
echo "🔐 Generating checksums..."
if [[ "$DRY_RUN" = false ]]; then
  mkdir -p "build/release/$VERSION"
  python -c "
import hashlib, os
rel_dir = r'build/release/$VERSION'
lines = []
for root, dirs, files in os.walk(rel_dir):
    for f in sorted(files):
        if f.endswith('.zip') or f.endswith('.tar.gz'):
            fp = os.path.join(root, f)
            rel_path = os.path.relpath(fp, rel_dir).replace('\\\\', '/')
            h = hashlib.sha256(open(fp, 'rb').read()).hexdigest()
            lines.append(f'{h}  {rel_path}')
out_file = os.path.join(rel_dir, 'SHA256SUMS.txt')
with open(out_file, 'w', encoding='utf-8') as out:
    out.write('\n'.join(lines) + '\n')
print(open(out_file, encoding='utf-8').read())
"
fi

# ─── Generate release metadata ───────────────────────
echo "📝 Generating metadata..."
if [[ "$DRY_RUN" = false ]]; then
  cat > "build/release/$VERSION/version.json" << EOF
{
  "version": "$VERSION",
  "builtAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "commitSha": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "commitShort": "$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')",
  "branch": "$(git branch --show-current 2>/dev/null || echo 'unknown')"
}
EOF
fi

# ─── Summary ──────────────────────────────────────────
echo ""
echo "✅ Release $VERSION built successfully!"
echo ""
echo "📁 Artifacts in: ./build/release/$VERSION/"
[[ "$DRY_RUN" = false ]] && ls -la "build/release/$VERSION/"
echo ""
echo "Next steps:"
echo "  1. Test the web app: open build/release/$VERSION/web/index.html"
echo "  2. Test wallpaper: open build/release/$VERSION/wallpaper/index.html?wallpaper=1"
echo "  3. Run: bash ./launch/code/verify-release.sh $VERSION"
echo "  4. Tag the release: git tag -a v$VERSION -m 'Release v$VERSION'"
echo "  5. Push: git push origin v$VERSION"

