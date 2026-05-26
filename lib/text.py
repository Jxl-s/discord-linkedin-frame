import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = Path(__file__).parent / "assets" / "Carlito-Bold.ttf"

def apply_arc_text(
    image: Image.Image,
    text: str,
    color=(255, 255, 255),
    font_size: int = 85,
    radius: int = 333,
    center=None,
    letter_spacing: float = 10,
    radius_offset: int = 2,
    center_angle_deg: float = 123.0,
    clockwise: bool = True,
    rotation_deg: float = 0.0,
) -> Image.Image:
    """
    Render text along a circular arc.

    Angle convention: 0° = right, 90° = down (screen/Y-down), 180° = left, 270° = up.
    center_angle_deg: angle where the text block is centered on the arc (135 = bottom-left).
    clockwise: direction of text travel on screen.
    rotation_deg: additional rotation of the entire arc around the center.
    radius_offset: shifts characters outward (+) or inward (-) from the arc circle.
    """
    img = image.convert("RGBA")
    w, h = img.size
    if center is None:
        center = (w // 2, h // 2)
    cx, cy = center

    font = ImageFont.truetype(str(FONT_PATH), font_size)

    # Visual clockwise on screen (Y-down) = decreasing angle in math convention
    direction = -1 if clockwise else 1

    # Use advance width (getlength) so spacing matches SVG text advancement
    char_widths = [font.getlength(ch) for ch in text]

    # Compute start angle so the text block is centered at center_angle_deg
    total_width = sum(char_widths) + letter_spacing * max(len(text) - 1, 0)
    total_arc_rad = total_width / radius
    center_rad = math.radians(center_angle_deg + rotation_deg)
    start_rad = center_rad - direction * total_arc_rad / 2

    text_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))

    arc_pos = 0.0
    for i, ch in enumerate(text):
        cw = char_widths[i]
        char_center_arc = arc_pos + cw / 2
        angle_rad = start_rad + direction * char_center_arc / radius

        r_eff = radius + radius_offset
        px = cx + r_eff * math.cos(angle_rad)
        py = cy + r_eff * math.sin(angle_rad)

        # Tangent angle in the direction of travel, converted to PIL rotation degrees
        tangent_rad = angle_rad + direction * math.pi / 2
        rotation = math.degrees(tangent_rad)

        # Render the character centered on a padded transparent canvas.
        # Use getbbox to find the visual bounds and center them at the arc point.
        bbox = font.getbbox(ch)
        glyph_w = bbox[2] - bbox[0]
        glyph_h = bbox[3] - bbox[1]
        pad = font_size
        canvas_w = max(int(cw), glyph_w) + pad * 2
        canvas_h = glyph_h + pad * 2
        char_img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        # Draw so the glyph's visual center aligns with the canvas center
        draw_x = pad + (canvas_w - pad * 2 - glyph_w) // 2 - bbox[0]
        draw_y = pad - bbox[1]
        ImageDraw.Draw(char_img).text((draw_x, draw_y), ch, font=font, fill=(*color, 255))

        # PIL.rotate rotates CCW by default, so negate to get the right orientation
        rotated = char_img.rotate(-rotation, expand=True, resample=Image.BICUBIC)

        rw, rh = rotated.size
        tmp = Image.new("RGBA", img.size, (0, 0, 0, 0))
        tmp.paste(rotated, (round(px - rw / 2), round(py - rh / 2)))
        text_layer = Image.alpha_composite(text_layer, tmp)

        arc_pos += cw + letter_spacing

    return Image.alpha_composite(img, text_layer)
