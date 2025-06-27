import os
import cv2
import json
import numpy as np
from board_scanner import scan_image
from overlays import draw_tile_overlay
from camera_utils import capture_image # use when user-capture is implemented in GUI
from tile_model import Tile, AnchorTile, ObjectTile
from board_model import BoardModel

def draw_all_overlays(img, tiles):
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
        # Draw original QR corners
        if "og_corners" in tile.attributes:
            pts = np.array(tile.attributes["og_corners"]).astype(int)
            cv2.polylines(img, [pts], True, (0, 255, 0), 2)

        draw_tile_overlay(img, tile)

def load_assets(tile_metadata_path):
    """
    Open file metadata that maps QR id to basic tile metadata
    Parameters:
        path (str): Path to the image file. 
    returns:
        json data
    """
    with open(tile_metadata_path) as f:
        return json.load(f)
    
def main():
    tile_metadata = load_assets("assets/tile_definitions.json") #may turn into arg that user can provide

    # Scan image and extract tile data
    image_path = "assets/tile_imgs/IMG_1611.jpg"
    img, tiles, hex_width = scan_image(image_path, tile_metadata=tile_metadata) #scan image for QR, return array of tile objects with tile position and id data
    

    # Create board of scanned tiles 
    board = BoardModel(tiles, hex_width=hex_width)
    board.print_adjacency_map()
    board.assign_zones() # assign anchors to children, children to anchors
    
    # cross_links = board.analyze_cross_zone_neighbors() #get relations between zones
    # for link in cross_links:
    #     print(link)

    # for tile in tiles:
    #     print(tile)

    #test
    # print("TILE BY ID:", board.get_tile_by_id("id_011"))

    print("TILE BY ID:", board.get_tile_neighbors_by_id("id_011"))
    
    # Draw and show annotated board img
    draw_all_overlays(img, tiles)
    cv2.imshow("Tile Mirror", img)
    print("Press any key to exit")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()