# 🛠️ Installer Build System

**Goal:** One-command reproducible installer builds for all platforms.

---

## 🔧 TOOLS REQUIRED

```bash
# macOS / Linux
brew install jq node npm imagemagick librsvg2-bin ffmpeg

# Or Debian/Ubuntu
sudo apt-get install -y jq nodejs npm imagemagick librsvg2-bin ffmpeg
```

---

## 📂 BUILD TARGETS

| Target | Format | Tool | Output |
|---|---|---|---|
| Web app | ZIP | Vite + zip | `primordials-web-v1.0.0.zip` |
| Wallpaper Engine | HTML + WebM | Custom | `primordials-wallpaper-v1.0.0.zip` |
| itch.io | ZIP | Vite + zip | `primordials-itch-v1.0.0.zip` |
| Windows | .exe (optional) | electron-builder | `PolygonalPrimordials-Setup-v1.0.0.exe` |
| macOS | .app / .pkg (optional) | electron-builder | `PolygonalPrimordials-v1.0.0.dmg` |
| Linux | .AppImage / .deb | electron-builder | `PolygonalPrimordials-v1.0.0.AppImage` |

---

## 🚀 ONE-COMMAND BUILD

```bash
# From project root
./code/build-release.sh 1.0.0

# This runs:
# 1. Clean
# 2. Install deps
# 3. Run typecheck
# 4. Run lint
# 5. Run tests
# 6. Build web app
# 7. Build wallpaper package
# 8. Build itch package
# 9. Generate checksums
# 10. Copy to release directory
```

See `code/build-release.sh` for the script.

---

## 🛠️ OPTIONAL: ELECTRON WRAPPER (Windows .exe)

For users who want a "double-click to run" experience without a browser.

```bash
# Install electron-builder
npm install -D electron electron-builder

# Configure (electron-builder.json)
{
  "appId": "io.gensoulslab.polygonalprimordials",
  "productName": "Polygonal Primordials",
  "directories": {
    "output": "build/electron"
  },
  "files": [
    "dist/**/*",
    "package.json"
  ],
  "win": {
    "target": "nsis",
    "icon": "launch/assets/icons/icon.ico"
  },
  "mac": {
    "target": "dmg",
    "icon": "launch/assets/icons/icon.icns"
  },
  "linux": {
    "target": "AppImage",
    "icon": "launch/assets/icons/icon-512.png"
  }
}

# Build
npx electron-builder --win --x64
```

Note: Electron wrapper is OPTIONAL for v1. Web app is the primary distribution. Add Electron wrapper in v1.1 if user feedback demands it.

---

## ✅ BUILD CHECKLIST

- [ ] `npm run build` succeeds (web app)
- [ ] `npm run build:wallpaper` succeeds (wallpaper)
- [ ] `npm run package:wallpaper` succeeds (Workshop package)
- [ ] Web ZIP unzips and runs
- [ ] Wallpaper ZIP works in Wallpaper Engine
- [ ] itch ZIP plays in itch.io HTML5 player
- [ ] All checksums generated
- [ ] All files under size limits
- [ ] Manifests and metadata correct
