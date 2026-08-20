import os, glob
from PIL import Image

src_dir = r'C:/Users/ASUS/Documents/Primodilas/Marketing/screenshots'
banners_dir = r'C:/Users/ASUS/Documents/Primodilas/Marketing/banners'
target_dirs = [
    r'C:/Users/ASUS/Documents/Primodilas/launch/assets/screenshots',
    r'C:/Users/ASUS/Documents/Primodilas/screenshotq',
    r'c:/Users/ASUS/Documents/DrunkIt/launch/assets/screenshotq',
    r'c:/Users/ASUS/Documents/DrunkIt/screenshots'
]

shots = {
    'screenshot-01-algae-bloom.png': os.path.join(src_dir, 'screenshot_01_heatmap.jpg'),
    'screenshot-02-deep-sea.png': os.path.join(src_dir, 'screenshot_04_aurora.jpg'),
    'screenshot-03-wallpaper-mode.png': os.path.join(src_dir, 'screenshot_aurora.jpg'),
    'screenshot-04-inspector-ui.png': os.path.join(src_dir, 'screenshot_03_inspector.jpg'),
    'screenshot-05-population-graph.png': os.path.join(src_dir, 'screenshot_02_speciation.jpg'),
    'screenshot-06-coral-reef.png': os.path.join(src_dir, 'screenshot_speciation.jpg'),
    'screenshot-07-volcanic-vent.png': os.path.join(src_dir, 'screenshot_heatmap.jpg'),
    'workshop-thumbnail.png': os.path.join(banners_dir, 'wallpaper_banner_16x9.jpg'),
    'itch-cover.png': os.path.join(banners_dir, 'itch_banner_3x2.jpg'),
    'header-capsule.png': os.path.join(banners_dir, 'header_capsule_460x215.jpg')
}

for td in target_dirs:
    os.makedirs(td, exist_ok=True)
    for name, src in shots.items():
        if os.path.exists(src):
            im = Image.open(src).convert('RGB')
            if name == 'itch-cover.png':
                img = im.resize((1280, 720), Image.Resampling.LANCZOS)
            elif name == 'header-capsule.png':
                img = im.resize((460, 215), Image.Resampling.LANCZOS)
            else:
                img = im.resize((1920, 1080), Image.Resampling.LANCZOS)
            out = os.path.join(td, name)
            img.save(out, format='PNG', optimize=True)
            print('Wrote', out)

print('Done screenshots')
