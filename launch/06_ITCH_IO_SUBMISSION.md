# 🎮 itch.io Submission

**Secondary launch channel — pay-what-you-want.**

---

## 📋 PAGE CONFIG

### Title
`	ext
Polygonal Primordials — A Living Ecosystem on Your Desktop
`

### Short text (~120 chars)
`	ext
A real ecosystem evolves on your screen. Watch predator and prey populations rise and fall. Free, open source, MIT.
`

### Description
`	ext
🌍 A LIVING ECOSYSTEM ON YOUR DESKTOP

Polygonal Primordials is a real-time artificial ecosystem simulation that turns your desktop into a window into a primordial world.

Every organism you see follows real ecological rules — prey graze, predators hunt, populations rise and fall. Six biomes included.

— KEY FEATURES —
🧬 Real-time ecosystem simulation
🌿 Six biomes (algae bloom, deep sea, primordial soup, tundra, coral reef, volcanic vent)
🖥️ Wallpaper mode — runs behind your desktop
🎮 Interactive controls — pause, speed, reset
💾 Local save — your world persists
🆓 Free, open source, MIT licensed
🛠️ Custom biomes via JSON
🌙 Auto-pauses when desktop is hidden

— TECH —
Built with React 18, TypeScript, Vite, and a custom ECS for the simulation. Canvas 2D rendering with WebGPU coming.

— ABOUT —
Polygonal Primordials is a solo passion project from Sahil Khutey (Gensouls Lab, Bilaspur, India).

— LINKS —
🌐 https://primordials.dev
💻 https://github.com/SahilKhutey/Primodials
💬 https://discord.gg/primordials
`

### Pricing
`	ext
No payment (Pay what you want, suggested )
`

### Tags
`	ext
simulation
wallpaper
ambient
screensaver
relaxing
ecology
open-source
cozy
art
generative
`

### Classification
`	ext
Games → Simulation
`

### Embed (optional)
Use the embed from storefronts/itch.io/EMBED.html

---

## 📂 FILES TO UPLOAD

Build the standalone ZIP from the web app:
`ash
# From project root
./code/package-itch.sh
# Produces: build/itch/primordials-v1.0.0-itch.zip
`

Contents of ZIP:
- index.html
- ssets/ (all bundled assets)
- README.txt (run instructions)
- iomes/ (sample biomes)

The ZIP should be <10MB (no source maps, no dev dependencies).

---

## 📂 FILE STRUCTURE INSIDE ZIP

`	ext
primordials/
├── index.html          # entry point
├── assets/
│   ├── index-[hash].js # bundled JS
│   ├── index-[hash].css # bundled CSS
│   └── ...             # images, fonts
├── biomes/
│   ├── algae-bloom.json
│   ├── deep-sea.json
│   └── ...             # (6 biomes)
└── README.txt
`

---

## ✅ SUBMISSION CHECKLIST

- [ ] Title and description match store listings
- [ ] Pricing set (PWYW with  suggestion)
- [ ] Cover image is 1280×720 (or itch will resize)
- [ ] Screenshots uploaded (5+)
- [ ] ZIP builds and runs locally
- [ ] Tested in itch.io's HTML5 player
- [ ] WebM version uploaded as fallback (optional)
- [ ] README.txt included with clear instructions
