# 🚀 Polygonal Primordials — Launch Package

**Status:** READY TO SHIP

This folder contains everything needed to launch v1.0.0 of Polygonal Primordials to the world.

---

## 📂 Contents

| File | Purpose |
|------|---------|
| `00_LAUNCH_PACKAGE_BRIEF.md` | Overview, timeline, success criteria |
| `01_APP_ICON_DESIGN.md` | Icon design spec |
| `02_APP_ICON_SVG.svg` | Vector icon master |
| `03_APP_ICON_PNG_SET.md` | PNG generation instructions |
| `04_STORE_SCREENSHOTS.md` | Screenshot capture + requirements |
| `05_WALLPAPER_ENGINE_SUBMISSION.md` | Workshop item config |
| `06_ITCH_IO_SUBMISSION.md` | itch.io page config |
| `07_GITHUB_RELEASE.md` | Tag + release process |
| `08_INSTALLER_BUILDS.md` | Build system overview |
| `09_LAUNCH_DAY_SCRIPT.md` | T-0 hour-by-hour script |
| `10_POST_LAUNCH_MONITORING.md` | 30-day monitoring plan |
| `code/build-release.sh` | One-command release builder |
| `code/package-wallpaper.sh` | Wallpaper package builder |
| `code/package-itch.sh` | itch.io package builder |
| `code/generate-icons.sh` | App icon generator |
| `code/verify-release.sh` | Pre-release smoke tests |

---

## 🚀 Quick Start

```bash
# 1. Generate app icons (requires rsvg-convert or similar)
./launch/code/generate-icons.sh

# 2. Build release artifacts
./launch/code/build-release.sh 1.0.0

# 3. Verify the build
./launch/code/verify-release.sh 1.0.0

# 4. Tag the release
git tag -s v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 5. Submit to stores
#   - Wallpaper Engine Workshop (WebM + Workshop item)
#   - itch.io (ZIP upload)
#   - GitHub Releases (artifacts)
```

---

## 📞 Contact

- 📧 [hello@primordials.dev](mailto:hello@primordials.dev)
- 💬 discord.gg/primordials

---

> "A quiet rebellion against static screens — shipping now."  
> — Sahil Khutey  
> Founder, Gensouls Lab  
> Bilaspur, India, 2026
