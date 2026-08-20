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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

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
python -c "
import json, os, sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
rel_dir = r'$RELEASE_DIR'
has_error = False
for root, dirs, files in os.walk(rel_dir):
    for f in sorted(files):
        if f.endswith('.json'):
            fp = os.path.join(root, f)
            try:
                with open(fp, 'r', encoding='utf-8') as jf:
                    json.load(jf)
                print(f'  ✅ {f}')
            except Exception as e:
                print(f'  ❌ INVALID JSON: {fp} ({e})')
                has_error = True
if has_error:
    sys.exit(1)
" || fail=1

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
python -c "
import zipfile, os, sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
rel_dir = r'$RELEASE_DIR'
has_error = False
for root, dirs, files in os.walk(rel_dir):
    for f in sorted(files):
        if f.endswith('.zip'):
            fp = os.path.join(root, f)
            try:
                with zipfile.ZipFile(fp, 'r') as zf:
                    corrupt = zf.testzip()
                    if corrupt:
                        print(f'  ❌ CORRUPT in {f}: {corrupt}')
                        has_error = True
                    else:
                        size_kb = os.path.getsize(fp) / 1024
                        print(f'  ✅ {f} ({size_kb:.1f} KB)')
            except Exception as e:
                print(f'  ❌ CORRUPT: {fp} ({e})')
                has_error = True
if has_error:
    sys.exit(1)
" || fail=1

# ─── Check checksums ──────────────────────────────────
echo ""
echo "🔐 Verifying checksums..."
if [[ -f "$RELEASE_DIR/SHA256SUMS.txt" ]]; then
  python -c "
import hashlib, os, sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
rel_dir = r'$RELEASE_DIR'
chk_file = os.path.join(rel_dir, 'SHA256SUMS.txt')
has_error = False
with open(chk_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        parts = line.split(None, 1)
        if len(parts) != 2: continue
        expected_hash, rel_path = parts[0], parts[1].strip()
        fp = os.path.join(rel_dir, rel_path)
        if not os.path.exists(fp):
            print(f'  ❌ Missing referenced file: {rel_path}')
            has_error = True
            continue
        calc_hash = hashlib.sha256(open(fp, 'rb').read()).hexdigest()
        if calc_hash == expected_hash:
            print(f'  ✅ {rel_path}: OK')
        else:
            print(f'  ❌ {rel_path}: HASH MISMATCH (expected {expected_hash}, got {calc_hash})')
            has_error = True
if has_error:
    sys.exit(1)
" || fail=1
else
  echo "  ⚠️ SHA256SUMS.txt not found"
  fail=1
fi

# ─── Headless browser test ────────────────────────────
echo ""
echo "🌐 Testing web build (headless)..."
python -c "
import http.server, socketserver, threading, time, urllib.request, os, sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')

web_dir = r'$WEB_DIR'
os.chdir(web_dir)

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args): pass

port = 8765
httpd = socketserver.TCPServer(('127.0.0.1', port), QuietHandler)
server_thread = threading.Thread(target=httpd.serve_forever)
server_thread.daemon = True
server_thread.start()

try:
    time.sleep(0.5)
    with urllib.request.urlopen(f'http://127.0.0.1:{port}/index.html', timeout=5) as res:
        if res.status == 200:
            print('  ✅ Web server responds 200')
        else:
            print(f'  ❌ Unexpected status: {res.status}')
            sys.exit(1)
finally:
    httpd.shutdown()
" || fail=1

# ─── Final ────────────────────────────────────────────
echo ""
if [[ $fail -eq 0 ]]; then
  echo "✅ All checks passed!"
  exit 0
else
  echo "❌ Some checks failed. Please review and re-run."
  exit 1
fi

