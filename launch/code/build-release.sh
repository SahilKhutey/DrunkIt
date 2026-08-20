#!/usr/bin/env bash
# build-release.sh — reproducible release for Polygonal Primordials
#
# Usage:
#   ./code/build-release.sh <version>              # full release
#   ./code/build-release.sh <version> --dry-run    # no artifacts written
#   ./code/build-release.sh <version> --skip-tests # NOT recommended
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

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "❌ Missing: $1"
    exit 1
  fi
}

require_command node
require_command npm
require_command git
require_command sha256sum

echo "🧬 Polygonal Primordials release builder"
echo "📦 Version: $VERSION"
echo "🔍 Dry run: $DRY_RUN"
echo ""

# ─── Clean ───────────────────────────────────────────
echo "🧹 Cleaning..."
[[ "$DRY_RUN" = false ]] && rm -rf build/release

# ─── Install deps ────────────────────────────────────
echo "📦 Installing dependencies..."
[[ "$DRY_RUN" = false ]] && npm ci

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
  bash ./code/package-wallpaper.sh "$VERSION"
fi

# ─── Build itch package ──────────────────────────────
echo "🎮 Building itch.io package..."
if [[ "$DRY_RUN" = false ]]; then
  bash ./code/package-itch.sh "$VERSION"
fi

# ─── Generate checksums ──────────────────────────────
echo "🔐 Generating checksums..."
if [[ "$DRY_RUN" = false ]]; then
  mkdir -p "build/release/$VERSION"
  find "build/release/$VERSION" -type f \( -name "*.zip" -o -name "*.tar.gz" \) -exec sha256sum {} \; > "build/release/$VERSION/SHA256SUMS.txt"
  cat "build/release/$VERSION/SHA256SUMS.txt"
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
echo "  3. Run: bash ./code/verify-release.sh $VERSION"
echo "  4. Tag the release: git tag -s v$VERSION -m 'Release v$VERSION'"
echo "  5. Push: git push origin v$VERSION"
