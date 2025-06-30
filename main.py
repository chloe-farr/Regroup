import os
import sys
import cv2
import json
import numpy as np
from core.board_scanner import scan_image, xray_board, cv2_to_pixmap
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
 

def rescan_board(img):
    """
        This function currently doesn't work
    """
    img_path = "assets/tile_imgs/IMG_1620.jpg"
    tile_metadata_path = "assets/tile_definitions.json" #may turn into arg that user can provide
    tile_attributes_path = "assets/tile_attributes.json"
    # Use the provided img, but reload metadata
    _, tile_data = load_assets(img_path, tile_metadata_path, tile_attributes_path)
    board = mock_board(img, tile_data)
    # Get and annotate your board image
    xray_img = xray_board(img, board.tiles)

    # Convert to pixmap
    xray_pixmap = cv2_to_pixmap(xray_img)

    return board, tile_data, xray_pixmap

def mock_board(img, tile_metadata):
    """
    Creates a mock board with hard-coded tiles and axial positions.

    Returns:
        Board: A Board object with mock data.
    """
    
    img, tiles, hex_width = scan_image(img, tile_metadata=tile_metadata) #scan image for QR, return array of tile objects with tile position and id data
    # board.print_adjacency_map()

    board = BoardModel(tiles, hex_width=hex_width)

    # xray_board(img, tsiles)
    
    return board

def merge_tile_metadata(definitions, attributes):
    """
    Combines static tile definitions with user-defined attributes.

    Parameters:
    - definitions (dict): Tile metadata from the scanner or definition file, keyed by QR ID (e.g., {"id_001": {"icon": "A"}}).
    - attributes (dict):   User-saved attribute data keyed by QR ID or icon (e.g., {"id_001": {"nickname": "Solar"}, "A": {...}}).

    Returns:
    - dict: Merged tile data keyed by QR ID, where user attributes override static definitions if any keys conflict.
    """
    merged = {}

    for qr_id, attrs in definitions.items():
        saved_attrs = attributes.get(qr_id, {})
        merged[qr_id] = {**attrs, **saved_attrs}  # saved overrides scanned

    return merged

def load_assets(img_path, tile_metadata_path, tile_attributes_path):
    # Scanned image of physical board
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"Image not found or couldn't be read: {img_path}")

    with open(tile_metadata_path) as f:
        tile_metadata = json.load(f)

    with open(tile_attributes_path) as f:
        tile_attributes = json.load(f)

    merged_tile_data = merge_tile_metadata(tile_metadata, tile_attributes)

    return img, merged_tile_data

def init_scanned_board_view(img, board):
        try:
            pixmap = xray_board(img, board.tiles)
            # print("success with bitmap")
            return pixmap
        except Exception as e:
            print("Pixmap conversion failed:", e)
            return

    # xray_pixmap = xray_board(img, board.tiles)


def main():
    app = QApplication(sys.argv)  # MUST be first Qt thing

    # Scanned image of physical board
    img_path = "assets/tile_imgs/IMG_1620.jpg"
    tile_metadata_path = "assets/tile_definitions.json" #may turn into arg that user can provide
    tile_attributes_path = "assets/tile_attributes.json"
    img, tile_data = load_assets(img_path, tile_metadata_path, tile_attributes_path)

    board = mock_board(img, tile_data)
    # print("Adjacency map:",board.adjacency_map)
    # print("TILE BY ID:", board.get_tile_by_id("id_007"))

    # print("TILE BY ID:", board.get_tile_neighbors_by_id("id_011"))

    # Get and annotate your board image
    xray_img = xray_board(img, board.tiles)

    # Convert to pixmap
    xray_pixmap = cv2_to_pixmap(xray_img)

    # Launch main window
    main_window = MainWindow(board, tile_data, COLOR_MAP, xray_pixmap, mock_board=rescan_board)
    main_window.show()

    sys.exit(app.exec())  # <--- this keeps the app running


if __name__ == "__main__":
    main()