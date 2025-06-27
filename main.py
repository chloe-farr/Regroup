import os
import sys
import cv2
import json
import numpy as np
from core.board_scanner import scan_image
from core.overlays import draw_tile_overlay
from core.camera_utils import capture_image # use when user-capture is implemented in GUI
from core.tile_model import Tile, AnchorTile, ObjectTile
from core.board_model import BoardModel
from gui.main_window import MainWindow
from gui.board_view import BoardView
from PyQt6.QtWidgets import QApplication
# Placeholder color map (same keys used in tile_attributes.json)
COLOR_MAP = {
    "red": "#FF6B6B",
    "blue": "#4D96FF",
    "green": "#55D187",
    "yellow": "#FFD93D",
    "purple": "#BFA2FF",
    "orange": "#FFAD5E",
    "pink": "#FF90B3",
    "teal": "#42C9C9"
}
 

def xray_board(img, tiles):
    """
    Draw polylines around original QR codes. This will give the user feedback on whether their tiles have scanned correctly.
    Parameters:
        path (str): Path to the image file.
        tile objects ([TILE]): to access corners of tile qr codes

    Returns:
        Nothing 
        
    Updates original image with polylines around QRs.
    """
    for tile in tiles:
        if "og_corners" in tile.attributes:
            pts = np.array(tile.attributes["og_corners"]).astype(int)
            cv2.polylines(img, [pts], True, (0, 255, 0), 2)

        draw_tile_overlay(img, tile)
    
    cv2.imshow("Tile Mirror", img)

def mock_board(img, tile_metadata):
    """
    Creates a mock board with hard-coded tiles and axial positions.

    Returns:
        Board: A Board object with mock data.
    """
    
    img, tiles, hex_width = scan_image(img, tile_metadata=tile_metadata) #scan image for QR, return array of tile objects with tile position and id data
    # board.print_adjacency_map()

    board = BoardModel(tiles, hex_width=hex_width)
    xray_board(img, tiles)
    
    return board

def load_assets(img_path, tile_metadata_path, tile_attributes_path):
    # Scanned image of physical board
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"Image not found or couldn't be read: {img_path}")

    with open(tile_metadata_path) as f:
        tile_metadata = json.load(f)

    with open(tile_attributes_path) as f:
        tile_attributes = json.load(f)

    return img, tile_metadata, tile_attributes


def main():
    app = QApplication(sys.argv)  # MUST be first Qt thing

    # Scanned image of physical board
    img_path = "assets/tile_imgs/IMG_1618.jpg"
    tile_metadata_path = "assets/tile_definitions.json" #may turn into arg that user can provide
    tile_attributes_path = "assets/tile_attributes.json"
    img, tile_metadata, tile_attributes = load_assets(img_path, tile_metadata_path, tile_attributes_path)

    board = mock_board(img, tile_metadata)
    
    # print("TILE BY ID:", board.get_tile_by_id("id_011"))

    # print("TILE BY ID:", board.get_tile_neighbors_by_id("id_011"))
    
    main_window = MainWindow(board, tile_attributes, COLOR_MAP)
    main_window.show()

    print("Press any key to exit")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()