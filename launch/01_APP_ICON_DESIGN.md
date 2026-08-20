# 🎨 Polygonal Primordials — App Icon Design Specification

## 🎯 CONCEPT

**Visual metaphor:** A single predator triangle chasing a single prey circle, framed by an orbital path — capturing the core "ecosystem in motion" idea in one glance.

**Why this works:**
- Reads at 16×16 (favicon size)
- Scales to 1024×1024 (app store master)
- Distinctive vs. competitors (most ambient/wallpaper apps are photos)
- Brand-aligned (uses primary palette)
- Works in monochrome

---

## 🎨 COLOR PALETTE

`	ext
Background:   #0F3D3E (Deep Teal)
Prey circle:  #F4F1DE (Bone White)
Predator:     #FF4FA3 (Magenta)
Orbital path: #F4F1DE @ 35% opacity
`

Optional biome accents (for variants):
- Coral: #FF6B6B
- Amber: #FFD93D
- Cyan: #4ECDC4

---

## 📐 COMPOSITION RULES

### Primary icon (1024×1024)
- **Padding:** 12% on all sides (safe area)
- **Background:** Rounded rectangle, 22% corner radius (matches macOS)
- **Circle (prey):** Centered, radius 18% of canvas
- **Triangle (predator):** Orbital position, 60° rotation from center
- **Orbital path:** Dashed ellipse, rotated 22°, stroke 1.5%

### Variants
- **Light variant:** Bone white background, deep teal organisms
- **Monochrome:** All white on transparent (for Linux/menus)
- **Adaptive:** Foreground (organisms) + background (deep teal) for Android

---

## ✨ DESIGN PRINCIPLES

1. **Recognizable at 16px** — must read in browser tabs
2. **Distinct silhouette** — works as silhouette/monochrome
3. **Brand consistent** — uses only brand palette
4. **No text** — icons should never contain text
5. **Centered composition** — circular, not asymmetric
6. **Subtle depth** — flat with one soft glow accent

---

## 🚫 WHAT TO AVOID

- ❌ Photorealistic renders (we're polygonal)
- ❌ Text or letters in the icon
- ❌ Busy compositions (too many organisms)
- ❌ Bright saturated colors (off-brand)
- ❌ Gradients in foreground (flat is on-brand)
- ❌ Real photographs
- ❌ Transparent backgrounds (use brand color)

---

## 📂 FILE OUTPUTS

Generate:
- icon-master-1024.svg (vector master)
- icon-master-1024.png (raster master)
- macOS .icns (multi-res: 16, 32, 64, 128, 256, 512, 1024)
- Windows .ico (multi-res: 16, 32, 48, 64, 128, 256)
- Linux PNG variants (16, 32, 48, 64, 128, 256, 512, 1024)
- Adaptive foreground + background (Android)
- Favicon set (already exists in brand/)
