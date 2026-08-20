# 🖼️ Polygonal Primordials — PNG Icon Set Specification

## 🎯 MASTER FILE

`	ext
icon-master-1024.svg    # Vector master (in repo)
icon-master-1024.png    # 1024×1024 PNG (rasterized from SVG)
`

Generate via:
`ash
# Using rsvg-convert
rsvg-convert -w 1024 -h 1024 icon-master-1024.svg -o icon-master-1024.png

# Or using Inkscape
inkscape icon-master-1024.svg --export-png=icon-master-1024.png -w 1024 -h 1024

# Or via online tool: https://cloudconvert.com/svg-to-png
`

---

## 📂 DELIVERABLE SIZES

### macOS (.icns — multi-resolution)

Required sizes:
- 16×16
- 32×32 (1× retina for 16)
- 64×64 (2× retina for 32)
- 128×128
- 256×256
- 512×512
- 1024×1024

Generate via:
`ash
# Using iconutil (macOS)
mkdir icon.iconset
for size in 16 32 64 128 256 512 1024; do
  rsvg-convert -w  -h  icon-master-1024.svg -o "icon.iconset/icon_x.png"
done
# Add @2x variants
cp icon.iconset/icon_32x32.png   icon.iconset/icon_16x16@2x.png
cp icon.iconset/icon_64x64.png   icon.iconset/icon_32x32@2x.png
cp icon.iconset/icon_256x256.png icon.iconset/icon_128x128@2x.png
cp icon.iconset/icon_512x512.png icon.iconset/icon_256x256@2x.png
cp icon.iconset/icon_1024x1024.png icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset -o icon.icns
`

### Windows (.ico — multi-resolution)

Required sizes:
- 16×16, 32×32, 48×48, 64×64, 128×128, 256×256

Generate via:
`ash
# Using ImageMagick
convert icon-master-1024.png \
  -define icon:auto-resize=16,32,48,64,128,256 \
  icon.ico
`

### Linux (PNG variants)

Required sizes:
- 16, 32, 48, 64, 128, 256, 512, 1024

Generate via:
`ash
for size in 16 32 48 64 128 256 512 1024; do
  rsvg-convert -w  -h  icon-master-1024.svg -o "icon-.png"
done
`

### Android Adaptive Icon

Required:
- oreground-1024×1024.png (transparent background, just organisms)
- ackground-1024×1024.png (just deep teal background)
- daptive-icon.xml (Android manifest)

`ash
# Foreground (just the organisms, transparent bg)
rsvg-convert -w 1024 -h 1024 \
  --background-color=none \
  -o foreground.png \
  icon-master-1024.svg
# Or extract via SVG manipulation
`

### Web Favicon Set (already produced in Phase 1)
- avicon.svg
- avicon-16x16.png
- avicon-32x32.png
- pple-touch-icon.png (180×180)
- ndroid-chrome-192x192.png
- ndroid-chrome-512x512.png
- mstile-150x150.png
- safari-pinned-tab.svg
- site.webmanifest

---

## 📂 DELIVERY FOLDER

`	ext
launch/assets/icons/
├── icon-master-1024.svg
├── icon-master-1024.png
├── icon.icns               # macOS
├── icon.ico                # Windows
├── icon-16.png
├── icon-32.png
├── icon-48.png
├── icon-64.png
├── icon-128.png
├── icon-256.png
├── icon-512.png
├── icon-1024.png
├── foreground-1024.png     # Android adaptive
├── background-1024.png     # Android adaptive
├── android-chrome-192x192.png # already in brand/
├── android-chrome-512x512.png # already in brand/
└── README.md               # generation instructions
`

---

## 🧪 VERIFICATION

Before shipping, verify:
- [ ] All sizes generated
- [ ] PNGs have no transparency (except Android foreground)
- [ ] Colors match brand palette exactly
- [ ] 16×16 is still recognizable
- [ ] 1024×1024 has no rendering artifacts
- [ ] File sizes are reasonable (<50KB for .icns)
