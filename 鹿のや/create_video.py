#!/usr/bin/env python3
"""鹿のや Instagram リール動画生成スクリプト（9:16縦型 + BGM + 明朝体）"""

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

# Fonts - Noto Serif JP (明朝体)
FONT_LIGHT = "/tmp/NotoSerifJP/SubsetOTF/JP/NotoSerifJP-Light.otf"
FONT_REGULAR = "/tmp/NotoSerifJP/SubsetOTF/JP/NotoSerifJP-Regular.otf"
FONT_SEMIBOLD = "/tmp/NotoSerifJP/SubsetOTF/JP/NotoSerifJP-SemiBold.otf"
FONT_BOLD = "/tmp/NotoSerifJP/SubsetOTF/JP/NotoSerifJP-Bold.otf"

# Caption animation styles
ANIM_FADE_UP = "fade_up"          # フェードイン + 下から上へスライド
ANIM_CHAR_BY_CHAR = "char_by_char"  # 一文字ずつ表示
ANIM_CENTER_EXPAND = "center_expand"  # 中央から左右に広がる
ANIM_FADE_ONLY = "fade_only"      # シンプルフェード
ANIM_TYPEWRITER = "typewriter"    # タイプライター風
ANIM_BLUR_IN = "blur_in"         # ぼかしからシャープに

# Slide-in directions for scene transitions
SLIDE_NONE = "none"
SLIDE_FROM_RIGHT = "from_right"
SLIDE_FROM_LEFT = "from_left"

# Scene definitions: (image_path, caption_lines, duration_sec, animation_style, slide_direction)
scenes = [
    (f"{WORK_DIR}/607198937741000790.jpg",
     ["鹿 の や", "", "— 春の訪れとともに —"],
     2.5, ANIM_CHAR_BY_CHAR, SLIDE_NONE),
    (f"{BASE_DIR}/7C1A5112.JPG",
     ["季節を纏うテーブル", "一皿の前に、もてなしは始まっている"],
     4, ANIM_FADE_UP, SLIDE_FROM_RIGHT),
    (f"{BASE_DIR}/7C1A5139.JPG",
     ["窓の向こうに広がる自然", "静寂が、最高の調味料になる"],
     4, ANIM_CENTER_EXPAND, SLIDE_FROM_LEFT),
    (f"{BASE_DIR}/7C1A5384.JPG",
     ["素材と向き合う手仕事", "火加減ひとつに、職人の矜持が宿る"],
     4, ANIM_TYPEWRITER, SLIDE_FROM_RIGHT),
    (f"{BASE_DIR}/7C1A5493.JPG",
     ["選び抜かれた一本", "料理と日本酒が織りなす余韻"],
     4, ANIM_FADE_UP, SLIDE_FROM_LEFT),
    (f"{BASE_DIR}/7C1A5507.JPG",
     ["カウンターに灯る温もり", "特別な夜を、ここで"],
     4, ANIM_BLUR_IN, SLIDE_FROM_RIGHT),
    (f"{BASE_DIR}/7C1A5112.JPG",  # End card uses table setting photo
     ["L'Artisan KANOYA", "", "詳細はプロフィールから"],
     3, ANIM_FADE_ONLY, SLIDE_NONE),
]


def create_sakura_bg():
    """Generate spring sakura background in 9:16 vertical format."""
    img = Image.new('RGB', (W, H))
    draw = ImageDraw.Draw(img)

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


def load_and_fit(path, target_w, target_h, extra_margin=0.15):
    """Load image and fit to target size with cover crop.
    extra_margin: load slightly larger for slide/pan room."""
    img = Image.open(path)
    img_w, img_h = img.size
    margin_w = int(target_w * (1 + extra_margin))
    margin_h = int(target_h * (1 + extra_margin))
    scale = max(margin_w / img_w, margin_h / img_h)
    new_w = int(img_w * scale)
    new_h = int(img_h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - margin_w) // 2
    top = (new_h - margin_h) // 2
    img = img.crop((left, top, left + margin_w, top + margin_h))
    return img


def apply_ken_burns_with_sway(img, frame_idx, total_frames,
                               zoom_start=1.0, zoom_end=1.08,
                               sway_amount=12):
    """Apply Ken Burns zoom + subtle organic sway (揺らぎ)."""
    t = frame_idx / max(total_frames - 1, 1)
    zoom = zoom_start + (zoom_end - zoom_start) * t

    img_w, img_h = img.size
    cw = int(W / zoom)
    ch = int(H / zoom)

    # Organic sway using sine waves at different frequencies
    sway_x = int(sway_amount * math.sin(t * math.pi * 2.5) * (1 - t * 0.3))
    sway_y = int(sway_amount * 0.6 * math.sin(t * math.pi * 1.8 + 0.7))

    cx = img_w // 2 + sway_x
    cy = img_h // 2 + sway_y

    left = max(0, cx - cw // 2)
    top = max(0, cy - ch // 2)
    right = min(img_w, left + cw)
    bottom = min(img_h, top + ch)

    # Adjust if we hit boundaries
    if right - left < cw:
        left = max(0, right - cw)
    if bottom - top < ch:
        top = max(0, bottom - ch)

    cropped = img.crop((left, top, left + cw, top + ch))
    return cropped.resize((W, H), Image.LANCZOS)


def apply_slide_transition(prev_frame, next_img, frame_idx, slide_frames,
                            direction, total_scene_frames):
    """Slide the new image in from left or right over a black/prev background."""
    t = frame_idx / max(slide_frames - 1, 1)
    ease_t = ease_out_cubic(t)

    # Get the current next frame with ken burns applied
    next_frame = apply_ken_burns_with_sway(next_img, 0, total_scene_frames)

    if direction == SLIDE_FROM_RIGHT:
        offset_x = int(W * (1 - ease_t))
    elif direction == SLIDE_FROM_LEFT:
        offset_x = int(-W * (1 - ease_t))
    else:
        return next_frame

    # Composite: prev_frame as background, next_frame sliding in
    result = prev_frame.copy()
    # Paste next frame at offset position
    if offset_x >= 0:
        # Sliding from right: paste the visible left portion of next_frame
        visible_w = W - offset_x
        crop_region = next_frame.crop((0, 0, visible_w, H))
        result.paste(crop_region, (offset_x, 0))
    else:
        # Sliding from left: paste the visible right portion of next_frame
        visible_w = W + offset_x
        crop_region = next_frame.crop((W - visible_w, 0, W, H))
        result.paste(crop_region, (0, 0))

    return result


def ease_out_cubic(t):
    """Cubic ease-out for smooth deceleration."""
    return 1 - (1 - t) ** 3


def ease_in_out_sine(t):
    """Sine ease-in-out for gentle motion."""
    return -(math.cos(math.pi * t) - 1) / 2


def draw_animated_caption(img, lines, frame_idx, total_frames, anim_style, is_end_card=False):
    """Draw caption with various animation styles."""
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_title = ImageFont.truetype(FONT_SEMIBOLD, 52)
    font_sub = ImageFont.truetype(FONT_LIGHT, 30)

    # Animation timing
    anim_in_frames = int(FPS * 1.2)   # 1.2s for text animation
    hold_frames = total_frames - anim_in_frames - int(FPS * 0.5)
    anim_out_start = total_frames - int(FPS * 0.5)

    # Overall opacity for fade out
    if frame_idx >= anim_out_start:
        master_opacity = 1.0 - ((frame_idx - anim_out_start) / (total_frames - anim_out_start))
    else:
        master_opacity = 1.0

    # Prepare line data
    line_data = []
    total_text_height = 0
    for idx, line in enumerate(lines):
        if not line:
            line_data.append(("", font_sub, 24))
            total_text_height += 24
            continue
        font = font_title if idx == 0 else font_sub
        bbox = draw.textbbox((0, 0), line, font=font)
        lh = bbox[3] - bbox[1] + 20
        line_data.append((line, font, lh))
        total_text_height += lh

    # Caption position - lower area safe for Reels
    if is_end_card:
        # End card: center vertically
        bar_top = (H - total_text_height) // 2 - 60
    else:
        bar_top = H - total_text_height - 300

    bar_height = total_text_height + 100

    # Semi-transparent background bar
    bar_opacity = int(140 * master_opacity)
    if anim_style == ANIM_CENTER_EXPAND:
        # Bar expands from center
        progress = min(1.0, frame_idx / anim_in_frames)
        progress = ease_out_cubic(progress)
        bar_w = int(W * progress)
        bar_left = (W - bar_w) // 2
        draw.rectangle(
            [(bar_left, bar_top), (bar_left + bar_w, bar_top + bar_height)],
            fill=(0, 0, 0, bar_opacity)
        )
    else:
        draw.rectangle(
            [(0, bar_top), (W, bar_top + bar_height)],
            fill=(0, 0, 0, bar_opacity)
        )

    # Draw each line with animation
    y = bar_top + 50
    for line_idx, (text, font, lh) in enumerate(line_data):
        if not text:
            y += lh
            continue

        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        base_x = (W - tw) // 2

        # Per-line stagger delay
        line_delay = line_idx * int(FPS * 0.3)
        local_frame = frame_idx - line_delay

        if local_frame < 0:
            y += lh
            continue

        line_progress = min(1.0, local_frame / anim_in_frames)

        if anim_style == ANIM_FADE_UP:
            # Fade in + slide up
            progress = ease_out_cubic(line_progress)
            text_opacity = int(240 * progress * master_opacity)
            offset_y = int(40 * (1 - progress))
            _draw_text_with_shadow(draw, base_x, y + offset_y, text, font, text_opacity)

        elif anim_style == ANIM_CHAR_BY_CHAR:
            # Character by character reveal
            total_chars = len(text)
            chars_shown = int(total_chars * min(1.0, local_frame / (anim_in_frames * 0.8)))
            visible_text = text[:chars_shown]
            if visible_text:
                text_opacity = int(240 * master_opacity)
                # Center the full text, but only draw visible portion
                _draw_text_with_shadow(draw, base_x, y, visible_text, font, text_opacity)

        elif anim_style == ANIM_CENTER_EXPAND:
            # Text fades in after bar expands
            if line_progress > 0.3:
                text_progress = min(1.0, (line_progress - 0.3) / 0.7)
                text_opacity = int(240 * ease_out_cubic(text_progress) * master_opacity)
                _draw_text_with_shadow(draw, base_x, y, text, font, text_opacity)

        elif anim_style == ANIM_TYPEWRITER:
            # Typewriter with cursor
            total_chars = len(text)
            char_progress = local_frame / (anim_in_frames * 0.7)
            chars_shown = min(total_chars, int(total_chars * char_progress))
            visible_text = text[:chars_shown]
            text_opacity = int(240 * master_opacity)
            if visible_text:
                _draw_text_with_shadow(draw, base_x, y, visible_text, font, text_opacity)
            # Blinking cursor
            if chars_shown < total_chars and (frame_idx // 8) % 2 == 0:
                cursor_bbox = draw.textbbox((0, 0), visible_text, font=font) if visible_text else (0, 0, 0, 0)
                cursor_x = base_x + (cursor_bbox[2] if visible_text else 0)
                draw.rectangle(
                    [(cursor_x + 4, y), (cursor_x + 7, y + lh - 20)],
                    fill=(255, 255, 255, text_opacity)
                )

        elif anim_style == ANIM_BLUR_IN:
            # Simple fade with scale illusion (slight vertical stretch)
            progress = ease_in_out_sine(line_progress)
            text_opacity = int(240 * progress * master_opacity)
            # Slight scale by adjusting y position
            scale_offset = int(8 * (1 - progress))
            _draw_text_with_shadow(draw, base_x, y - scale_offset, text, font, text_opacity)

        elif anim_style == ANIM_FADE_ONLY:
            # Simple elegant fade
            progress = ease_in_out_sine(line_progress)
            text_opacity = int(240 * progress * master_opacity)
            _draw_text_with_shadow(draw, base_x, y, text, font, text_opacity)

        y += lh

    # Decorative line for elegance (thin gold line)
    if master_opacity > 0:
        line_y = bar_top + 42
        line_opacity = int(120 * master_opacity)
        line_progress = min(1.0, frame_idx / anim_in_frames)
        line_w = int(200 * ease_out_cubic(line_progress))
        line_left = (W - line_w) // 2
        if line_w > 0:
            draw.rectangle(
                [(line_left, line_y), (line_left + line_w, line_y + 1)],
                fill=(212, 175, 125, line_opacity)
            )
            # Bottom decorative line
            bottom_line_y = bar_top + bar_height - 42
            draw.rectangle(
                [(line_left, bottom_line_y), (line_left + line_w, bottom_line_y + 1)],
                fill=(212, 175, 125, line_opacity)
            )

    img_rgba = img.convert('RGBA')
    composited = Image.alpha_composite(img_rgba, overlay)
    return composited.convert('RGB')


def _draw_text_with_shadow(draw, x, y, text, font, opacity):
    """Draw text with subtle shadow for depth."""
    if opacity <= 0:
        return
    # Shadow
    shadow_opacity = int(opacity * 0.4)
    draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, shadow_opacity))
    draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, int(shadow_opacity * 0.6)))
    # Main text
    draw.text((x, y), text, font=font, fill=(255, 255, 255, opacity))


def create_end_card_image(base_img):
    """Create a darkened, blurred end card from a photo."""
    # Darken the image
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Brightness(base_img)
    dark = enhancer.enhance(0.3)
    # Add slight blur for dreamy effect
    dark = dark.filter(ImageFilter.GaussianBlur(radius=6))
    return dark


def create_fade(frame1, frame2, t):
    """Create crossfade between two frames."""
    return Image.blend(frame1, frame2, t)


def main():
    print(f"Output size: {W}x{H} (Instagram Reels 9:16)")
    print(f"Font: Noto Serif JP (明朝体)")

    # Regenerate sakura background in vertical format
    print("Generating sakura background (9:16)...")
    create_sakura_bg()

    frame_num = 0
    slide_frames = int(FPS * 0.7)  # 0.7s slide-in transition
    fade_frames = int(FPS * 0.8)   # 0.8s crossfade fallback
    prev_last_frame = None

    for scene_idx, (img_path, caption, duration, anim_style, slide_dir) in enumerate(scenes):
        total_frames = int(duration * FPS)
        is_end_card = (scene_idx == len(scenes) - 1)
        print(f"Scene {scene_idx + 1}/{len(scenes)}: {caption[0]} [{anim_style}] slide={slide_dir} ({total_frames} frames)")

        if img_path:
            base_img = load_and_fit(img_path, W, H)
            if is_end_card:
                base_img = create_end_card_image(base_img)
        else:
            base_img = Image.new('RGB', (W, H), (25, 22, 20))

        for i in range(total_frames):
            # Apply Ken Burns with organic sway
            frame = apply_ken_burns_with_sway(base_img, i, total_frames)

            # Caption (delay caption start slightly during slide-in)
            caption_delay = slide_frames if (prev_last_frame and slide_dir != SLIDE_NONE) else 0
            caption_frame = max(0, i - caption_delay)
            caption_total = total_frames - caption_delay
            if caption_frame >= 0 and caption_total > 0:
                frame = draw_animated_caption(
                    frame, caption, caption_frame, caption_total, anim_style, is_end_card
                )

            # Scene transition: slide-in or crossfade
            if prev_last_frame and i < slide_frames:
                if slide_dir != SLIDE_NONE:
                    frame = apply_slide_transition(
                        prev_last_frame, base_img, i, slide_frames,
                        slide_dir, total_frames
                    )
                else:
                    t = i / fade_frames
                    frame = create_fade(prev_last_frame, frame, min(1.0, t))

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

    # Cleanup frames
    import shutil
    shutil.rmtree(FRAME_DIR)
    print("Frames cleaned up.")


if __name__ == "__main__":
    main()
