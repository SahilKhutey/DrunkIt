# 🚀 GitHub Release Process

---

## 🛠️ TAG + RELEASE

`ash
# 1. Ensure clean working tree
git status

# 2. Update CHANGELOG.md
# Move "Unreleased" to "v1.0.0"
# Add release date

# 3. Commit the changelog update
git add CHANGELOG.md
git commit -m "chore: prepare v1.0.0 release"

# 4. Tag the release
git tag -s v1.0.0 -m "Release v1.0.0 — first public release"

# 5. Push the tag
git push origin v1.0.0
`

---

## 📝 GITHUB RELEASE NOTES

### Title
`	ext
v1.0.0 — First Public Release
`

### Body
`markdown
# Polygonal Primordials v1.0.0 — First Public Release

**Release date:** [DATE]

This is the first public release of Polygonal Primordials, a living desktop ecosystem simulation.

## What's new

This is the initial release. Six biomes, wallpaper support, interactive simulation.

## Verified features

- 🧬 Real-time ecosystem simulation (predator-prey dynamics)
- 🌿 Six biomes included
- 🖥️ Live wallpaper mode
- 🎮 Interactive controls (pause, speed, reset)
- 💾 Local save/load (offline-first)
- 🔗 World sharing via seed code
- 🆓 Free, open source, MIT

## What's NOT in this release

- ❌ Multiplayer (planned for v2.x)
- ❌ Steam release (planned after market validation)
- ❌ Mobile version (planned for v3.x)
- ❌ Native C++ standalone (planned for v4.x)

## Install

### Web app (any platform)
Download primordials-web-v1.0.0.zip below, unzip, open index.html.

### Wallpaper Engine (Windows/Linux)
Subscribe on Steam Workshop: [Workshop link]

### itch.io
[Download page]

## Verified performance

Tested on:
- Windows 10/11 (Chrome, Firefox, Edge)
- macOS 12+ (Safari, Chrome)
- Ubuntu 22.04+ (Chrome, Firefox)

60 FPS at 250 entities on mid-range hardware.

## Known issues

- [list known issues from GitHub Issues]

## Thanks

To everyone who tested, gave feedback, and waited patiently.  
This is the start, not the finish.
`

---

## 📂 RELEASE ARTIFACTS TO UPLOAD

`	ext
v1.0.0/
├── primordials-web-v1.0.0.zip        # Web app standalone
├── primordials-wallpaper-v1.0.0.zip  # Wallpaper Engine package
├── primordials-itch-v1.0.0.zip       # itch.io ready
├── SHA256SUMS.txt                    # Checksums
└── v1.0.0-source.tar.gz              # Source tarball
`

Generate SHA-256 checksums:
`ash
sha256sum *.zip *.tar.gz > SHA256SUMS.txt
`

---

## ✅ CHECKLIST

- [ ] CHANGELOG.md updated
- [ ] Tag created and signed
- [ ] Release notes drafted
- [ ] All artifacts uploaded
- [ ] Checksums generated
- [ ] Marked as "Latest release" (automatic if it's the highest semver)
