# 🎨 Wallpaper Engine Workshop Submission

**This is the primary launch channel.**

---

## 📋 WORKSHOP ITEM CONFIG

### Title
`	ext
Polygonal Primordials — Living Ecosystem
`

### Description
`	ext
A real ecosystem that evolves on your desktop.

Six biomes from peaceful ponds to volcanic vents. Predator and prey populations rise and fall according to real ecological rules.

• 60 FPS even on modest hardware
• Pause, resume, speed control from Wallpaper pause menu
• Auto-pauses when desktop is hidden
• Saves your world locally every 60 seconds
• Share a world with friends via a simple code

Built by a solo developer in Bilaspur, India. Open source, MIT.

Free for Wallpaper Engine subscribers. No account required.

GitHub: github.com/SahilKhutey/Primodials
Discord: discord.gg/primordials
`

### Tags
`	ext
Animated
Live Wallpaper
Ambient
Relaxing
Screensaver
Nature
Science
Minimalist
Loopable
Procedural
Dark
Cool
`

### Visibility
`	ext
Public
`

### Price
`	ext
Free
`

### Compatibility
`	ext
Type: Video (we ship as a self-contained HTML/WebM)
Audio: None
Pause when maximized: Yes
Pause when other app is focused: Yes
`

### Preview Image
- Use Screenshot 3 (wallpaper mode) — 1920×1080 PNG, <500KB

### Preview Video
- 30-second loop, 1080p H.264, <30MB
- Shows: biome running, populations changing, pause behavior

---

## 📂 FILE TO UPLOAD

Workshop accepts:
- WebM video (preferred — auto-pause via Workshop UI)
- HTML page (interactive — pause via our own UI)

**Recommended:** WebM video loop for maximum compatibility.  
**Alternative:** HTML wrapper that loads the web app.

For HTML upload:
`html
<!-- index.html — workshop entry -->
<!DOCTYPE html>
<html>
<head>
  <title>Polygonal Primordials</title>
  <style>html,body{margin:0;background:#0A0908;overflow:hidden}</style>
</head>
<body>
  <iframe
    src="https://primordials.dev/?wallpaper=1&biome=algae-bloom&fps=60"
    style="width:100vw;height:100vh;border:none;display:block"
    allow="autoplay"
  ></iframe>
</body>
</html>
`

Note: WebM is preferred because:
- No network dependency
- Workshop can apply its own pause logic
- Lower CPU usage than running JS

But HTML allows interactivity (clicking, pausing, settings).  
**Recommendation:** Ship WebM for Workshop, keep the HTML version as a bonus.

---

## 🔄 GENERATING THE WEBM LOOP

`ash
# 1. Run simulation for 60s, capture as MP4
# OBS Studio → Display Capture → 1920×1080 → 60s → Save as raw.mp4

# 2. Convert to WebM (loop)
ffmpeg -i raw.mp4 \
  -c:v libvpx-vp9 -crf 30 -b:v 0 \
  -pix_fmt yuv420p \
  -deadline good \
  -row-mt 1 \
  -tile-columns 2 \
  -frame-parallel 1 \
  -auto-alt-ref 1 \
  -lag-in-frames 25 \
  -loop 0 \
  primordials-wallpaper.webm

# Verify file size (should be <30MB for 60s)
ls -lh primordials-wallpaper.webm
`

---

## ✅ SUBMISSION CHECKLIST

- [ ] Title matches store listing
- [ ] Description uses verified claims only
- [ ] Tags are accurate (no spam tags)
- [ ] Thumbnail is real product
- [ ] Preview video loops seamlessly
- [ ] File size within limits
- [ ] Compatibility flags correct
- [ ] Test on real Wallpaper Engine install before submitting
