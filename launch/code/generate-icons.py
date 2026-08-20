#!/usr/bin/env python3
import math, os, sys, struct, io, shutil
from PIL import Image, ImageDraw

def render_icon(master_size=1024, supersample=4, render_bg=True, render_fg=True):
    ss = supersample
    size = master_size * ss
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if render_bg:
        bg_color = (15, 61, 62, 255)
        radius = int(225 * ss)
        draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=bg_color)
        
        glow_cx, glow_cy = 512 * ss, 410 * ss
        glow_r = int(614 * ss)
        glow_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)
        for r in range(glow_r, 0, -int(4 * ss)):
            alpha = int(0.6 * 255 * (1.0 - (r / glow_r) ** 1.5))
            if alpha > 0:
                glow_draw.ellipse([glow_cx - r, glow_cy - r, glow_cx + r, glow_cy + r], fill=(26, 77, 78, int(alpha * 0.15)))
        img = Image.alpha_composite(img, glow_img)
        draw = ImageDraw.Draw(img)

    if render_fg:
        cx, cy = 512 * ss, 512 * ss
        rx, ry = 340 * ss, 140 * ss
        rot = math.radians(-22)
        
        dash_on = 14 * ss
        dash_off = 22 * ss
        cycle = dash_on + dash_off
        
        num_steps = 1000
        points = []
        for i in range(num_steps + 1):
            t = (2 * math.pi * i) / num_steps
            ex = rx * math.cos(t)
            ey = ry * math.sin(t)
            rx_rot = ex * math.cos(rot) - ey * math.sin(rot)
            ry_rot = ex * math.sin(rot) + ey * math.cos(rot)
            points.append((cx + rx_rot, cy + ry_rot))
            
        orbit_color = (244, 241, 222, int(255 * 0.35))
        stroke_w = max(1, int(6 * ss))
        dist = 0
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i+1]
            seg_len = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            rem = dist % cycle
            if rem < dash_on:
                draw.line([p1, p2], fill=orbit_color, width=stroke_w)
            dist += seg_len

        prey_r = 100 * ss
        prey_color = (244, 241, 222, 255)
        draw.ellipse([cx - prey_r, cy - prey_r, cx + prey_r, cy + prey_r], fill=prey_color)

        dot_r = 24 * ss
        dot_color = (15, 61, 62, 255)
        draw.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=dot_color)

        def rotate_point(x, y, angle_rad):
            return x * math.cos(angle_rad) - y * math.sin(angle_rad), x * math.sin(angle_rad) + y * math.cos(angle_rad)

        def transform_poly(pts, tx, ty, angle_deg, s):
            rad = math.radians(angle_deg)
            res = []
            for px, py in pts:
                rx, ry = rotate_point(px * s, py * s, rad)
                res.append((tx * s + rx, ty * s + ry))
            return res

        pred1_pts = [(0, 0), (92, 46), (92, -46)]
        pred1_trans = transform_poly(pred1_pts, 820, 512, 20, ss)
        draw.polygon(pred1_trans, fill=(255, 79, 163, 255))

        pred2_pts = [(0, 0), (50, 25), (50, -25)]
        pred2_trans = transform_poly(pred2_pts, 204, 540, -160, ss)
        draw.polygon(pred2_trans, fill=(255, 79, 163, int(255 * 0.6)))

    return img.resize((master_size, master_size), Image.Resampling.LANCZOS)

def make_icns(png_dict):
    entries = []
    for tag, data in png_dict.items():
        entry_len = len(data) + 8
        entries.append(tag.encode('ascii') + struct.pack('>I', entry_len) + data)
    body = b''.join(entries)
    header = b'icns' + struct.pack('>I', len(body) + 8)
    return header + body

def generate(source_svg='launch/02_APP_ICON_SVG.svg', out_dir='launch/assets/icons'):
    os.makedirs(out_dir, exist_ok=True)
    master_icon = render_icon(1024, supersample=4, render_bg=True, render_fg=True)
    foreground_icon = render_icon(1024, supersample=4, render_bg=False, render_fg=True)
    background_icon = render_icon(1024, supersample=4, render_bg=True, render_fg=False)

    master_icon.save(os.path.join(out_dir, 'icon-master-1024.png'), 'PNG')
    master_icon.save(os.path.join(out_dir, 'icon-1024.png'), 'PNG')
    foreground_icon.save(os.path.join(out_dir, 'foreground-1024.png'), 'PNG')
    background_icon.save(os.path.join(out_dir, 'background-1024.png'), 'PNG')

    png_bytes_map = {}
    for size, tag in [(16, 'icp4'), (32, 'icp5'), (64, 'icp6'), (128, 'ic07'), (256, 'ic08'), (512, 'ic09'), (1024, 'ic10')]:
        resized = master_icon.resize((size, size), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        resized.save(buf, format='PNG')
        png_bytes_map[tag] = buf.getvalue()

    for size in [16, 32, 48, 64, 128, 256, 512]:
        resized = master_icon.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(os.path.join(out_dir, f'icon-{size}.png'), 'PNG')

    master_icon.save(os.path.join(out_dir, 'icon.ico'), format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
    
    with open(os.path.join(out_dir, 'icon.icns'), 'wb') as f:
        f.write(make_icns(png_bytes_map))

    if os.path.exists(source_svg):
        shutil.copy2(source_svg, os.path.join(out_dir, 'icon-master-1024.svg'))

    print(f'Generated icons in {out_dir}')

if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else 'launch/02_APP_ICON_SVG.svg'
    out = sys.argv[2] if len(sys.argv) > 2 else 'launch/assets/icons'
    generate(src, out)
