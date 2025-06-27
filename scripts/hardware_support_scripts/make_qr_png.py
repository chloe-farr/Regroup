# uses SVGs of letters as identifiers based on the Teachers font https://fonts.google.com/specimen/Teachers/about
## Teachers-VariableFont_wght.ttf
# pip install segno pillow
# pip install qrcode[pil]
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
# ==== CONFIGURATION ====
letter = "A"
qr_data = "id_001_1"
icon_font_size = 210  # Increased for better visibility
icon_border = 8       # Thickness of outline
icon_length = 100    # 1/2 width of white background rectangle
output_filename = "qr_with_bold_icon.png"
font_filename = "Andika-Bold.ttf"
# font = ImageFont.truetype("Verdana Bold", icon_font_size)

# ==== File Paths ====
base_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(base_dir, font_filename)
output_path = os.path.join(base_dir, output_filename)

# ==== QR Setup ====
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=0,
)
qr.add_data(qr_data)
qr.make(fit=True)
qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

# Target output size
image_size = 600
qr_margin = 20
qr_target_size = image_size - 2 * qr_margin
qr_img = qr_img.resize((qr_target_size, qr_target_size), Image.NEAREST)

# Create canvas and paste QR
canvas = Image.new("RGB", (image_size, image_size), "white")
canvas.paste(qr_img, (qr_margin, qr_margin))

# ==== Icon Drawing ====
draw = ImageDraw.Draw(canvas)
font = ImageFont.truetype(font_path, icon_font_size)
center = (image_size // 2, image_size // 2)

# # Draw black border (larger square)
draw.rectangle(
    (center[0] - icon_length - icon_border, center[1] - icon_length - icon_border,
     center[0] + icon_length + icon_border, center[1] + icon_length + icon_border),
    fill="black"
)

# Draw white inner square (background for icon)
draw.rectangle(
    (center[0] - icon_length, center[1] - icon_length,
     center[0] + icon_length, center[1] + icon_length),
    fill="white"
)

# Calculate letter position
bbox = draw.textbbox((0, 0), letter, font=font)
text_pos = (
    center[0] - (bbox[2] + bbox[0]) // 2,
    center[1] - (bbox[3] + bbox[1]) // 2
)

# Center letter on top
draw.text(text_pos, letter, font=font, fill="black")

# ==== Save ====
canvas.save(output_path)
print(f"QR code saved to: {output_path}")


"""
qr_with_bold_icon_A1: 
letter = "A"
icon_font_size = 210  # Increased for better visibility
icon_border = 8       # Thickness of outline
icon_length = 100    # 1/2 width of white background rectangle
font_filename = "Teachers-ExtraBold.ttf"

# Draw black border (larger square)
draw.rectangle(
    (center[0] - icon_length - icon_border, center[1] - icon_length - icon_border,
     center[0] + icon_length + icon_border, center[1] + icon_length + icon_border),
    fill="black"
)

# Draw white inner square (background for icon)
draw.rectangle(
    (center[0] - icon_length, center[1] - icon_length,
     center[0] + icon_length, center[1] + icon_length),
    fill="white"
)
"""

"""
qr_with_bold_icon_A2: 
letter = "A"
icon_font_size = 210  # Increased for better visibility
icon_border = 8       # Thickness of outline
icon_length = 100    # 1/2 width of white background rectangle
font_filename = "Teachers-ExtraBold.ttf"

# Draw white inner square (background for icon)
draw.rectangle(
    (center[0] - icon_length, center[1] - icon_length,
     center[0] + icon_length, center[1] + icon_length),
    fill="white"
)

# no black fill box

# Calculate letter position
bbox = draw.textbbox((0, 0), letter, font=font)
text_pos = (
    center[0] - (bbox[2] + bbox[0]) // 2,
    center[1] - (bbox[3] + bbox[1]) // 2
)
"""

"""
qr_with_bold_icon_A3: 
letter = "A"
icon_font_size = 210  # Increased for better visibility
icon_border = 8       # Thickness of outline
icon_length = 100    # 1/2 width of white background rectangle
font_filename = "Teachers-Regular.ttf"

# Draw white inner square (background for icon)
draw.rectangle(
    (center[0] - icon_length, center[1] - icon_length,
     center[0] + icon_length, center[1] + icon_length),
    fill="white"
)

# no black fill box

# Calculate letter position
bbox = draw.textbbox((0, 0), letter, font=font)
text_pos = (
    center[0] - (bbox[2] + bbox[0]) // 2,
    center[1] - (bbox[3] + bbox[1]) // 2
)
"""

"""
qr_with_bold_icon_A4: 
letter = "A"
icon_font_size = 210  # Increased for better visibility
icon_border = 8       # Thickness of outline
icon_length = 100    # 1/2 width of white background rectangle
font_filename = "Teachers-Regular.ttf"

# Draw black border (larger square)
draw.rectangle(
    (center[0] - icon_length - icon_border, center[1] - icon_length - icon_border,
     center[0] + icon_length + icon_border, center[1] + icon_length + icon_border),
    fill="black"
)

# Draw white inner square (background for icon)
draw.rectangle(
    (center[0] - icon_length, center[1] - icon_length,
     center[0] + icon_length, center[1] + icon_length),
    fill="white"
)

# Calculate letter position
bbox = draw.textbbox((0, 0), letter, font=font)
text_pos = (
    center[0] - (bbox[2] + bbox[0]) // 2,
    center[1] - (bbox[3] + bbox[1]) // 2
)
"""

"""
qr_with_bold_icon_A5: 
letter = "A"
icon_font_size = 210  # Increased for better visibility
icon_border = 8       # Thickness of outline
icon_length = 100    # 1/2 width of white background rectangle
font = ImageFont.truetype("Verdana", icon_font_size)

# Draw black border (larger square)
draw.rectangle(
    (center[0] - icon_length - icon_border, center[1] - icon_length - icon_border,
     center[0] + icon_length + icon_border, center[1] + icon_length + icon_border),
    fill="black"
)

# Draw white inner square (background for icon)
draw.rectangle(
    (center[0] - icon_length, center[1] - icon_length,
     center[0] + icon_length, center[1] + icon_length),
    fill="white"
)
"""

"""
qr_with_bold_icon_A6: 
letter = "A"
icon_font_size = 210  # Increased for better visibility
icon_border = 8       # Thickness of outline
icon_length = 100    # 1/2 width of white background rectangle
font = ImageFont.truetype("Verdana Bold", icon_font_size)

# Draw black border (larger square)
draw.rectangle(
    (center[0] - icon_length - icon_border, center[1] - icon_length - icon_border,
     center[0] + icon_length + icon_border, center[1] + icon_length + icon_border),
    fill="black"
)

# Draw white inner square (background for icon)
draw.rectangle(
    (center[0] - icon_length, center[1] - icon_length,
     center[0] + icon_length, center[1] + icon_length),
    fill="white"
)
"""


"""
qr_with_bold_icon_A7: 
letter = "a"
icon_font_size = 210  # Increased for better visibility
icon_border = 8       # Thickness of outline
icon_length = 100    # 1/2 width of white background rectangle
font_filename = "Teachers-Regular.ttf"

# Draw black border (larger square)
draw.rectangle(
    (center[0] - icon_length - icon_border, center[1] - icon_length - icon_border,
     center[0] + icon_length + icon_border, center[1] + icon_length + icon_border),
    fill="black"
)

# Draw white inner square (background for icon)
draw.rectangle(
    (center[0] - icon_length, center[1] - icon_length,
     center[0] + icon_length, center[1] + icon_length),
    fill="white"
)
"""

"""
qr_with_bold_icon_A8: 
letter = "a"
icon_font_size = 210  # Increased for better visibility
icon_border = 8       # Thickness of outline
icon_length = 100    # 1/2 width of white background rectangle
font_filename = "Teachers-ExtraBold.ttf"

# Draw black border (larger square)
draw.rectangle(
    (center[0] - icon_length - icon_border, center[1] - icon_length - icon_border,
     center[0] + icon_length + icon_border, center[1] + icon_length + icon_border),
    fill="black"
)

# Draw white inner square (background for icon)
draw.rectangle(
    (center[0] - icon_length, center[1] - icon_length,
     center[0] + icon_length, center[1] + icon_length),
    fill="white"
)
"""


"""
qr_with_bold_icon_A9: 
letter = "a"
icon_font_size = 210  # Increased for better visibility
icon_border = 8       # Thickness of outline
icon_length = 100    # 1/2 width of white background rectangle
font = ImageFont.truetype("Verdana Bold", icon_font_size)

# Draw black border (larger square)
draw.rectangle(
    (center[0] - icon_length - icon_border, center[1] - icon_length - icon_border,
     center[0] + icon_length + icon_border, center[1] + icon_length + icon_border),
    fill="black"
)

# Draw white inner square (background for icon)
draw.rectangle(
    (center[0] - icon_length, center[1] - icon_length,
     center[0] + icon_length, center[1] + icon_length),
    fill="white"
)
"""

"""
qr_with_bold_icon_A10: 
letter = "a"
icon_font_size = 210  # Increased for better visibility
icon_border = 8       # Thickness of outline
icon_length = 100    # 1/2 width of white background rectangle
font_filename = "Andika-Bold.ttf"

# Draw black border (larger square)
draw.rectangle(
    (center[0] - icon_length - icon_border, center[1] - icon_length - icon_border,
     center[0] + icon_length + icon_border, center[1] + icon_length + icon_border),
    fill="black"
)

# Draw white inner square (background for icon)
draw.rectangle(
    (center[0] - icon_length, center[1] - icon_length,
     center[0] + icon_length, center[1] + icon_length),
    fill="white"
)
"""