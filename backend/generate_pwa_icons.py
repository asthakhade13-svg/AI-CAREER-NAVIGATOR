import os
from PIL import Image, ImageDraw

def generate_icons():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    icons_dir = os.path.join(root_dir, "icons")
    frontend_icons_dir = os.path.join(root_dir, "frontend", "icons")
    os.makedirs(icons_dir, exist_ok=True)
    os.makedirs(frontend_icons_dir, exist_ok=True)

    # 1. Generate SVG Icon
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e1b4b" />
      <stop offset="50%" stop-color="#312e81" />
      <stop offset="100%" stop-color="#4f46e5" />
    </linearGradient>
    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f59e0b" />
      <stop offset="100%" stop-color="#fbbf24" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>
  <!-- Background Rounded Squircle -->
  <rect width="512" height="512" rx="128" fill="url(#bgGrad)" />
  
  <!-- Outer Compass Ring -->
  <circle cx="256" cy="256" r="180" fill="none" stroke="#6366f1" stroke-width="4" stroke-dasharray="8 6" opacity="0.6" />
  <circle cx="256" cy="256" r="160" fill="none" stroke="#818cf8" stroke-width="2" opacity="0.4" />
  
  <!-- Compass Star North -->
  <polygon points="256,76 276,236 256,216" fill="url(#goldGrad)" filter="url(#glow)" />
  <polygon points="256,76 236,236 256,216" fill="#d97706" />
  
  <!-- Compass Star South -->
  <polygon points="256,436 276,276 256,296" fill="#4338ca" />
  <polygon points="256,436 236,276 256,296" fill="#312e81" />
  
  <!-- Compass Star East -->
  <polygon points="436,256 276,276 296,256" fill="url(#goldGrad)" />
  <polygon points="436,256 276,236 296,256" fill="#d97706" />
  
  <!-- Compass Star West -->
  <polygon points="76,256 236,276 216,256" fill="#4338ca" />
  <polygon points="76,256 236,236 216,256" fill="#312e81" />
  
  <!-- Center Core Ring & Gem -->
  <circle cx="256" cy="256" r="32" fill="#1e1b4b" stroke="#f59e0b" stroke-width="6" />
  <circle cx="256" cy="256" r="14" fill="#ffffff" />
</svg>'''

    for d in [icons_dir, frontend_icons_dir]:
        with open(os.path.join(d, "icon.svg"), "w", encoding="utf-8") as f:
            f.write(svg_content)

    # 2. Helper to draw PNG icons via Pillow
    def draw_icon(size, is_maskable=False):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Background
        # Draw background rectangle
        bg_color = (30, 27, 75, 255) # #1e1b4b
        corner_r = 0 if is_maskable else int(size * 0.22)
        
        if is_maskable:
            draw.rectangle([0, 0, size, size], fill=bg_color)
        else:
            draw.rounded_rectangle([0, 0, size, size], radius=corner_r, fill=bg_color)

        # Scale factor
        scale = size / 512.0
        cx, cy = size / 2.0, size / 2.0

        # Secondary background gradient glow circle
        glow_r = int(210 * scale)
        draw.ellipse([cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r], fill=(49, 46, 129, 255))
        
        inner_bg_r = int(180 * scale)
        draw.ellipse([cx - inner_bg_r, cy - inner_bg_r, cx + inner_bg_r, cy + inner_bg_r], fill=(67, 56, 202, 255))

        # Compass Outer Rings
        ring_r1 = int(170 * scale)
        draw.ellipse([cx - ring_r1, cy - ring_r1, cx + ring_r1, cy + ring_r1], outline=(129, 140, 248, 160), width=max(2, int(3 * scale)))
        
        ring_r2 = int(150 * scale)
        draw.ellipse([cx - ring_r2, cy - ring_r2, cx + ring_r2, cy + ring_r2], outline=(99, 102, 241, 120), width=max(1, int(2 * scale)))

        # 4 Compass Points (North, South, East, West)
        # North
        n_tip = (cx, cy - 165 * scale)
        n_left = (cx - 24 * scale, cy - 24 * scale)
        n_right = (cx + 24 * scale, cy - 24 * scale)
        center = (cx, cy)
        draw.polygon([n_tip, n_right, center], fill=(245, 158, 11, 255)) # Gold light
        draw.polygon([n_tip, n_left, center], fill=(217, 119, 6, 255))   # Gold dark

        # South
        s_tip = (cx, cy + 165 * scale)
        s_left = (cx - 24 * scale, cy + 24 * scale)
        s_right = (cx + 24 * scale, cy + 24 * scale)
        draw.polygon([s_tip, s_right, center], fill=(79, 70, 229, 255))
        draw.polygon([s_tip, s_left, center], fill=(49, 46, 129, 255))

        # East
        e_tip = (cx + 165 * scale, cy)
        e_top = (cx + 24 * scale, cy - 24 * scale)
        e_bottom = (cx + 24 * scale, cy + 24 * scale)
        draw.polygon([e_tip, e_bottom, center], fill=(251, 191, 36, 255))
        draw.polygon([e_tip, e_top, center], fill=(217, 119, 6, 255))

        # West
        w_tip = (cx - 165 * scale, cy)
        w_top = (cx - 24 * scale, cy - 24 * scale)
        w_bottom = (cx - 24 * scale, cy + 24 * scale)
        draw.polygon([w_tip, w_bottom, center], fill=(79, 70, 229, 255))
        draw.polygon([w_tip, w_top, center], fill=(49, 46, 129, 255))

        # Center Emblem Ring
        center_ring_r = int(34 * scale)
        draw.ellipse([cx - center_ring_r, cy - center_ring_r, cx + center_ring_r, cy + center_ring_r], 
                     fill=(30, 27, 75, 255), outline=(245, 158, 11, 255), width=max(2, int(5 * scale)))

        # Center White Star / Gem
        gem_r = int(14 * scale)
        draw.ellipse([cx - gem_r, cy - gem_r, cx + gem_r, cy + gem_r], fill=(255, 255, 255, 255))

        return img

    # Generate 192x192, 512x512, and maskable 512x512
    img_192 = draw_icon(192, is_maskable=False)
    img_512 = draw_icon(512, is_maskable=False)
    img_maskable = draw_icon(512, is_maskable=True)

    for d in [icons_dir, frontend_icons_dir]:
        img_192.save(os.path.join(d, "icon-192.png"), "PNG")
        img_512.save(os.path.join(d, "icon-512.png"), "PNG")
        img_maskable.save(os.path.join(d, "icon-maskable.png"), "PNG")

    print("[SUCCESS] Generated all PWA icons (icon.svg, icon-192.png, icon-512.png, icon-maskable.png) in root and frontend!")

if __name__ == "__main__":
    generate_icons()
