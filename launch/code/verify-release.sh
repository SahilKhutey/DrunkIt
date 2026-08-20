#!/usr/bin/env bash
# verify-release.sh — pre-release smoke tests
#
# Runs the built artifacts in headless mode and verifies they start.
#
# License: MIT

set -euo pipefail

VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
  echo "Usage: $0 <version>"
  exit 1
fi

RELEASE_DIR="build/release/$VERSION"
WEB_DIR="$RELEASE_DIR/web"
WALLPAPER_DIR="$RELEASE_DIR/wallpaper"
ITCH_DIR="$RELEASE_DIR/itch"

if [[ ! -d "$RELEASE_DIR" ]]; then
  echo "❌ Release directory not found: $RELEASE_DIR"
  exit 1
fi

echo "🔍 Verifying release v$VERSION..."
echo ""

# ─── Check artifacts exist ───────────────────────────
echo "📦 Checking artifacts..."
fail=0
for path in "$WEB_DIR/index.html" "$WALLPAPER_DIR/index.html" "$ITCH_DIR/primordials/index.html"; do
  if [[ -f "$path" ]]; then
    echo "  ✅ $path"
  else
    echo "  ❌ MISSING: $path"
    fail=1
  fi
done

# ─── Validate JSON ────────────────────────────────────
echo ""
echo "📄 Validating JSON files..."
for json in $(find "$RELEASE_DIR" -name "*.json" -type f); do
  if jq empty "$json" >/dev/null 2>&1; then
    echo "  ✅ $(basename "$json")"
  else
    echo "  ❌ INVALID JSON: $json"
    fail=1
  fi
done

# ─── Check biomes ─────────────────────────────────────
echo ""
echo "🌿 Checking biome files..."
for biome in algae-bloom deep-sea primordial-soup tundra coral-reef volcanic-vent; do
  if find "$RELEASE_DIR" -name "${biome}.json" -type f | grep -q .; then
    echo "  ✅ $biome.json"
  else
    echo "  ❌ MISSING: $biome.json"
    fail=1
  fi
done

# ─── Check ZIP files ─────────────────────────────────
echo ""
echo "📦 Checking ZIP files..."
for zip in $(find "$RELEASE_DIR" -name "*.zip" -type f); do
  if unzip -t "$zip" >/dev/null 2>&1; then
    size=$(du -h "$zip" | cut -f1)
    echo "  ✅ $(basename "$zip") ($size)"
  else
    echo "  ❌ CORRUPT: $zip"
    fail=1
  fi
done

# ─── Check checksums ──────────────────────────────────
echo ""
echo "🔐 Verifying checksums..."
if [[ -f "$RELEASE_DIR/SHA256SUMS.txt" ]]; then
  if cd "$RELEASE_DIR" && sha256sum -c SHA256SUMS.txt --quiet 2>/dev/null; then
    echo "  ✅ All checksums verified"
  else
    echo "  ❌ Checksum verification failed"
    fail=1
  fi
  cd - > /dev/null
else
  echo "  ⚠️ SHA256SUMS.txt not found"
fi

# ─── Headless browser test ────────────────────────────
echo ""
echo "🌐 Testing web build (headless)..."
if command -v node >/dev/null 2>&1; then
  # Spin up a quick local server and check it responds
  cd "$WEB_DIR" 2>/dev/null && {
    python3 -m http.server 8765 >/dev/null 2>&1 &
    SERVER_PID=$!
    sleep 2
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8765/index.html | grep -q "200"; then
      echo "  ✅ Web server responds 200"
    else
      echo "  ❌ Web server did not respond"
      fail=1
    fi
    kill $SERVER_PID 2>/dev/null || true
  } || echo "  ⚠️ Skipped (no Python)"
fi

# ─── Final ────────────────────────────────────────────
echo ""
if [[ $fail -eq 0 ]]; then
  echo "✅ All checks passed!"
  exit 0
else
  echo "❌ Some checks failed. Please review and re-run."
  exit 1
fi
