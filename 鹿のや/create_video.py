#!/usr/bin/env python3
"""鹿のや Instagram リール動画生成スクリプト（9:16縦型 + BGM）"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import subprocess
import os
import math
import random

BASE_DIR = "/home/user/0328Artisan-Kanoya"
WORK_DIR = f"{BASE_DIR}/鹿のや"
FRAME_DIR = f"{WORK_DIR}/frames"
BGM_PATH = f"{BASE_DIR}/Sovereign_Bloom.mp3"
os.makedirs(FRAME_DIR, exist_ok=True)

# Instagram Reels: 1080x1920 (9:16)
W, H = 1080, 1920
FPS = 30

# Scene definitions: (image_path, caption_lines, duration_sec)
scenes = [
    (f"{WORK_DIR}/sakura_spring.jpg",
     ["鹿 の や", "", "— 春の訪れとともに —"],
     4),
    (f"{BASE_DIR}/7C1A5112.JPG",
     ["季節を纏うテーブル", "一皿の前に、もてなしは始まっている"],
     4),
    (f"{BASE_DIR}/7C1A5139.JPG",
     ["窓の向こうに広がる自然", "静寂が、最高の調味料になる"],
     4),
    (f"{BASE_DIR}/7C1A5384.JPG",
     ["素材と向き合う手仕事", "火加減ひとつに、職人の矜持が宿る"],
     4),
    (f"{BASE_DIR}/7C1A5493.JPG",
     ["選び抜かれた一本", "料理とワインが奏でるハーモニー"],
     4),
    (f"{BASE_DIR}/7C1A5507.JPG",
     ["カウンターに灯る温もり", "特別な夜を、ここで"],
     4),
    (None,  # End card
     ["鹿 の や", "", "ご予約・お問い合わせはお気軽に"],
     3),
]


def find_font():
    """Find a Japanese-capable font."""
    font_paths = [
        "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            return p
    import glob
    cjk = glob.glob("/usr/share/fonts/**/Noto*CJK*", recursive=True)
    if cjk:
        return cjk[0]
    return None


def create_sakura_bg():
    """Generate spring sakura background in 9:16 vertical format."""
    img = Image.new('RGB', (W, H))
    draw = ImageDraw.Draw(img)

    # Soft spring gradient
    for y in range(H):
        r = int(255 - (y / H) * 40)
        g = int(210 + (y / H) * 30)
        b = int(230 + (y / H) * 25)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    random.seed(42)

    def draw_petal(draw, cx, cy, size, angle, color):
        points = []
        for i in range(20):
            t = i / 20 * 2 * math.pi
            r = size * (0.5 + 0.5 * math.cos(t)) * (0.3 + 0.7 * abs(math.sin(t)))
            x = cx + r * math.cos(t + angle)
            y = cy + r * math.sin(t + angle)
            points.append((x, y))
        if len(points) > 2:
            draw.polygon(points, fill=color)

    for _ in range(150):
        cx = random.randint(-50, W + 50)
        cy = random.randint(-50, H + 50)
        size = random.randint(20, 70)
        angle = random.uniform(0, 2 * math.pi)
        pink = random.randint(200, 255)
        g = random.randint(150, 200)
        b = random.randint(180, 220)
        af = random.uniform(0.4, 1.0)
        color = (int(pink * af + 255 * (1 - af)),
                 int(g * af + 220 * (1 - af)),
                 int(b * af + 235 * (1 - af)))
        draw_petal(draw, cx, cy, size, angle, color)

    for _ in range(250):
        cx = random.randint(0, W)
        cy = random.randint(0, H)
        size = random.randint(3, 14)
        color = (random.randint(240, 255), random.randint(180, 210), random.randint(200, 225))
        draw.ellipse([cx - size, cy - size // 2, cx + size, cy + size // 2], fill=color)

    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    img.save(f"{WORK_DIR}/sakura_spring.jpg", quality=90)
    return img


def load_and_fit(path, target_w, target_h):
    """Load image and fit to target size with cover crop."""
    img = Image.open(path)
    img_w, img_h = img.size

    scale = max(target_w / img_w, target_h / img_h)
    new_w = int(img_w * scale)
    new_h = int(img_h * scale)

    img = img.resize((new_w, new_h), Image.LANCZOS)

    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    img = img.crop((left, top, left + target_w, top + target_h))
    return img


def apply_ken_burns(img, frame_idx, total_frames, zoom_start=1.0, zoom_end=1.08):
    """Apply subtle Ken Burns (zoom) effect."""
    t = frame_idx / max(total_frames - 1, 1)
    zoom = zoom_start + (zoom_end - zoom_start) * t

    cw = int(W / zoom)
    ch = int(H / zoom)
    left = (W - cw) // 2
    top = (H - ch) // 2

    cropped = img.crop((left, top, left + cw, top + ch))
    return cropped.resize((W, H), Image.LANCZOS)


def draw_caption(img, lines, font_path, opacity=220):
    """Draw caption text with semi-transparent background at bottom."""
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        font_large = ImageFont.truetype(font_path, 48) if font_path else ImageFont.load_default()
        font_small = ImageFont.truetype(font_path, 30) if font_path else ImageFont.load_default()
    except Exception:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    total_height = 0
    line_data = []
    for line in lines:
        if not line:
            line_data.append(("", font_small, 20))
            total_height += 20
            continue
        font = font_large if line == lines[0] else font_small
        bbox = draw.textbbox((0, 0), line, font=font)
        lh = bbox[3] - bbox[1] + 18
        line_data.append((line, font, lh))
        total_height += lh

    # Position caption in lower third (safe area for Reels)
    bar_top = H - total_height - 280
    bar_height = total_height + 80
    draw.rectangle(
        [(0, bar_top), (W, bar_top + bar_height)],
        fill=(0, 0, 0, int(opacity * 0.55))
    )

    y = bar_top + 40
    for text, font, lh in line_data:
        if not text:
            y += lh
            continue
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        # Text shadow
        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, int(opacity * 0.5)))
        draw.text((x, y), text, font=font, fill=(255, 255, 255, opacity))
        y += lh

    img_rgba = img.convert('RGBA')
    composited = Image.alpha_composite(img_rgba, overlay)
    return composited.convert('RGB')


def create_fade(frame1, frame2, t):
    """Create crossfade between two frames."""
    return Image.blend(frame1, frame2, t)


def create_end_card():
    """Create ending card with dark elegant background."""
    img = Image.new('RGB', (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        v = int(25 + (y / H) * 15)
        draw.line([(0, y), (W, y)], fill=(v, v - 3, v - 5))
    return img


def main():
    font_path = find_font()
    print(f"Using font: {font_path}")
    print(f"Output size: {W}x{H} (Instagram Reels 9:16)")

    # Regenerate sakura background in vertical format
    print("Generating sakura background (9:16)...")
    create_sakura_bg()

    frame_num = 0
    fade_frames = int(FPS * 0.8)
    prev_last_frame = None

    for scene_idx, (img_path, caption, duration) in enumerate(scenes):
        total_frames = int(duration * FPS)
        print(f"Scene {scene_idx + 1}/{len(scenes)}: {caption[0]} ({total_frames} frames)")

        if img_path:
            base_img = load_and_fit(img_path, W, H)
        else:
            base_img = create_end_card()

        for i in range(total_frames):
            frame = apply_ken_burns(base_img, i, total_frames)

            if i < FPS:
                cap_opacity = int(220 * (i / FPS))
            elif i > total_frames - FPS // 2:
                cap_opacity = int(220 * ((total_frames - i) / (FPS // 2)))
            else:
                cap_opacity = 220

            cap_opacity = max(0, min(255, cap_opacity))
            if cap_opacity > 0:
                frame = draw_caption(frame, caption, font_path, cap_opacity)

            if prev_last_frame and i < fade_frames:
                t = i / fade_frames
                frame = create_fade(prev_last_frame, frame, t)

            frame.save(f"{FRAME_DIR}/frame_{frame_num:05d}.jpg", quality=85)
            frame_num += 1

            if i == total_frames - 1:
                prev_last_frame = frame

    print(f"Total frames: {frame_num}")

    # Encode to MP4 with BGM
    output_path = f"{WORK_DIR}/shikanoya_spring_reel.mp4"
    video_duration = frame_num / FPS

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", f"{FRAME_DIR}/frame_%05d.jpg",
        "-i", BGM_PATH,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-af", f"afade=t=in:st=0:d=2,afade=t=out:st={video_duration - 2}:d=2",
        "-shortest",
        "-movflags", "+faststart",
        output_path
    ]
    print("Encoding MP4 with BGM...")
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"Reel video created: {output_path}")

    # Also remove old horizontal video
    old_video = f"{WORK_DIR}/shikanoya_spring.mp4"
    if os.path.exists(old_video):
        os.remove(old_video)
        print(f"Removed old video: {old_video}")

    # Cleanup frames
    import shutil
    shutil.rmtree(FRAME_DIR)
    print("Frames cleaned up.")


if __name__ == "__main__":
    main()
