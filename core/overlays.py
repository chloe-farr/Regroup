import cv2


def draw_tile_overlay(img, tile):
    """
    Draw additional information on scanned tile image

    Parameters:
        path (str): Path to the image file. 
    
    Returns: None

    Updates original image with circles at tile centres, text for self ID and Anchor ID
    """
    x, y = map(int, tile.centroid)
    cv2.circle(img, (x, y), 24, (255, 255, 70), -1)

    # Icon label
    label = tile.icon() if callable(tile.icon) else str(tile.icon)
    cv2.putText(img, label, (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

    # Anchor of object in-zone
    if hasattr(tile, "assigned_to") and tile.assigned_to:
        cv2.putText(img, f" {tile.assigned_to}", (x + 10, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

    # Anchor's child count
    if hasattr(tile, "children") and tile.children:
        count = len(tile.children)
        cv2.putText(img, f"{count}", (x - 30, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)