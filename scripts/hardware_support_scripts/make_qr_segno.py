import segno
import svgwrite
from pathlib import Path
import os

def createQR(letter: str, data: str):
    print(f"Generating: letter={letter}, data={data}")

    # ---------- CONSTANTS ----------
    canvas_px = 146            # full hex-face size in px
    font_size = 73             # Teachers letter height
    qr_border_px = 5              # thick border around QR
    qr_sz = 70
    canvas_border_px = 1              # thin border around whole tile
    teachers_ttf = "Andika-Bold.ttf"
    font_family_name = "Andika Bold"
    out_svg = f"qr_icon_vector_{data}_AndikaB.svg"
    # --------------------------------

    # ---- Paths & font embedding ----
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    font_path = Path(base_dir).parent / "fonts" / teachers_ttf
    qr_path = Path(base_dir).parent / "QRs" 
    output_path = os.path.join(qr_path, out_svg)

    dwg = svgwrite.Drawing(output_path, size=(canvas_px, canvas_px))
    dwg.embed_font(font_family_name, str(font_path))   # pass *string* path

    # ------------- LETTER -----------
    letter_x = canvas_px / 2
    letter_y = font_size*0.85                # rough optical centre for uppercase
    dwg.add(dwg.text(
        letter,
        insert=(letter_x, letter_y),
        text_anchor="middle",
        font_family=font_family_name,
        font_size=font_size,
        fill="black"
    ))

    # ------------- QR CODE ----------
    #   1) build matrix without quiet zone
    qr = segno.make(data, error="H")
    border_sz = 0.1  # Quiet zone to remove
    # matrix = [row[border_sz:-border_sz] for row in qr.matrix[border_sz:-border_sz]]
    matrix = list(qr.matrix)
    m_count = len(matrix)  # Number of modules (e.g., 29)

    qr_px = 70  # Target height in pixels
    module_px = qr_px / m_count  # Size of each module in pixels

    qr_origin_x = (canvas_px - qr_px) / 2  # Center horizontally
    qr_origin_y = (canvas_px - qr_px)*0.9        # Align bottom
    
    for y, row in enumerate(matrix):
        for x, cell in enumerate(row):
            if cell:
                dwg.add(dwg.rect(
                    insert=(qr_origin_x + x * module_px, qr_origin_y + y * module_px),
                    size=(module_px, module_px),
                    fill='black'
                ))

    

    # QR border rectangle
    # dwg.add(dwg.rect(
    #     insert=(qr_origin_x - qr_border_px/2,
    #             qr_origin_y - qr_border_px/2),
    #     size=(qr_px + qr_border_px,
    #           qr_px + qr_border_px),
    #     fill="none",
    #     stroke="black",
    #     stroke_width=qr_border_px
    # ))

    # # -------- canvas-wide border ----
    # dwg.add(dwg.rect(
    #     insert=(0, 0),
    #     size=(canvas_px, canvas_px),
    #     fill="none",
    #     stroke="black",
    #     stroke_width=canvas_border_px
    # ))

    dwg.save()
    print(f"Saved   : {output_path}\n")

# ----------------- DEMO -----------------
letters   = ["A", "B", "C", "E", "F", "G"]
id_base   = "id_"
counter   = 0

for i in range(3):
    for letter in letters:
        data_id = f"{id_base}{counter:03}"
        createQR(letter, data_id)
        counter += 1

    
for i in range(4):
    data_id = f"{id_base}{counter:03}"  # Formats 0 → "000", 1 → "001", etc.
    createQR("O", data_id)
    counter += 1