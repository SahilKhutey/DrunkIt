# 📸 Polygonal Primordials — Store Screenshots

**All screenshots must depict the ACTUAL PRODUCT, not concept art.**

---

## 📐 STEAM SCREENSHOTS (1920×1080, minimum 5)

### Screenshot 1 — Hero shot
**Caption:** Algae Bloom biome — peak biodiversity moment  
**Capture:** Run Algae Bloom for 60s, screenshot at peak

### Screenshot 2 — Deep Sea
**Caption:** Deep Sea biome — bioluminescent abyss  
**Capture:** Switch biome, wait 30s, screenshot

### Screenshot 3 — Wallpaper Mode
**Caption:** Running as a desktop wallpaper behind real desktop icons  
**Capture:** Set as wallpaper, screenshot actual desktop

### Screenshot 4 — UI
**Caption:** Biome selector + settings panel  
**Capture:** Open settings, screenshot UI

### Screenshot 5 — Population Graph
**Caption:** Real-time population dynamics over 5 minutes  
**Capture:** Show the in-app graph (if implemented) or annotated screenshot

### Screenshot 6 (optional) — Ultrawide
**Caption:** Ultrawide display (21:9) support  
**Capture:** Run on ultrawide screen

---

## 📐 WALLPAPER ENGINE WORKSHOP THUMBNAIL

**Recommended:** 1920×1080 PNG
- Use the most visually striking biome at its peak
- Must show actual product output (no concept art)
- Compress to < 500 KB for Workshop

---

## 📐 ITCH.IO COVER IMAGE

**Recommended:** 1280×720 PNG
- Lighter on UI, heavier on biome atmosphere
- Include project name overlay (small, corner)
- Use Algae Bloom or Coral Reef

---

## 📐 PRESS KIT SCREENSHOTS

For press kits, use the same Steam shots but in higher quality.  
**Never** use placeholder or concept images.

---

## 📐 YOUTUBE THUMBNAIL (Dev Log)

**Recommended:** 1280×720 PNG
- Big bold text: "Dev Log #1"
- Small game logo
- Ecosystem still as background
- High contrast

---

## 🛠️ CAPTURE SCRIPT

`ash
#!/usr/bin/env bash
# capture-screenshots.sh
# Run app, capture each biome at peak, save to screenshots/
set -euo pipefail

mkdir -p screenshots

# Run app
npm run dev &
APP_PID=$!
sleep 10  # let app start

# Capture each biome (manual step — adjust biome, capture, save)
for biome in algae-bloom deep-sea primordial-soup tundra coral-reef volcanic-vent; do
  echo "Switch to biome: "
  echo "Press ENTER when ready to capture..."
  read -r
  scrot -d 5 "screenshots/-hero.png" || \
    screencapture -w 1920 -h 1080 "screenshots/-hero.png"
done

# Cleanup
kill  2>/dev/null || true
echo "✅ Captured  screenshots"
`

Or use the in-app capture (Phase 1 added useScreenshot capability).

---

## ✅ CHECKLIST BEFORE SHIPPING

- [ ] All screenshots show real product (no concept art)
- [ ] All are 1920×1080 minimum
- [ ] No identifiable personal information visible
- [ ] No debug overlays
- [ ] No placeholder text
- [ ] Compressed (<500KB each)
- [ ] Filename descriptive: screenshot--{biome}--{shot}.png
