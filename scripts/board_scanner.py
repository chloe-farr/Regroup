import cv2
import math
import numpy as np
from tile_model import create_tile

"""
Scans image only.
See "scan_qr_test.py for scanning with active camera
"""

def dist(p1, p2):
    """Use the Euclidean distance between adjacent pairs"""
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def calculate_square_side(corners):
    # print("Corners raw:", corners)
    # print("Shape:", np.array(corners).shape)
    
    """Estimates average side length of a quadrilateral by averaging the lengths of all four edges."""
    cx = sum(x for x, _ in corners) / 4
    cy = sum(y for _, y in corners) / 4

    # Sort corners around centroid
    corners = list(corners)  # Ensure it's a list, not a NumPy array
    corners.sort(key=lambda c: math.atan2(c[1] - cy, c[0] - cx))

    sides = [dist(corners[i], corners[(i + 1) % 4]) for i in range(4)]
    
    return sum(sides) / 4  # average in case of distortion


def rotate_point(p, origin, angle_rad):
    """
    Rotates a point p around a given origin by angle_rad radians.
    """
    ox, oy = origin
    px, py = p
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    qx = ox + cos_a * (px - ox) - sin_a * (py - oy)
    qy = oy + sin_a * (px - ox) + cos_a * (py - oy)
    return [qx, qy]

def get_rotation_angle(corners):
    """
    Computes the rotation angle (in radians and degrees) of a square QR code,
    snapping to the nearest multiple of 60 degrees.
    """
    tl, tr = np.array(corners[0]), np.array(corners[1])
    dx, dy = tr - tl
    angle_rads = math.atan2(dy, dx)
    rot_deg = (math.degrees(angle_rads) + 360) % 360

    # Snap to nearest multiple of 60
    snapped_deg = round(rot_deg / 60) * 60 % 360

    return -angle_rads, snapped_deg  # Negated angle_rads to restore upright orientation

def normalize_square(corners):
    """
    Returns 4 corners rotated around centre of square so they are visually upright
    """
    angle_rad, rot_deg = get_rotation_angle(corners)
    qr_origin = np.mean(corners, axis=0)  # rotate around visual center
    qr_size = calculate_square_side(corners)

    return qr_size, angle_rad, rot_deg, qr_origin

def rotate_offset(offset_vector, angle_rad):
    """
    Get offset vector of the 
    """
    rot_matrix = np.array([
        [math.cos(angle_rad), -math.sin(angle_rad)],
        [math.sin(angle_rad),  math.cos(angle_rad)]
    ])
    offset_vector = np.array(offset_vector).reshape((2,))  # Ensure it's a flat 1D array
    return rot_matrix @ offset_vector  # Matrix-vector multiplication



def regulate_tile(corners):
    """
    Rotates a QR tile upright and calculates:
    - its rotation angle
    - the center of its containing hex tile (based on fixed offset)
    - the QR corners repositioned as if rotated around the hex tile center

    Arguments:
        data: The decoded QR data (optional)
        corners: List or array of 4 QR corners (each a [x, y] point)

    Returns:
        tile_rot_deg (float): Rotation angle in degrees
        hex_center (np.ndarray): New hex tile center position (2D)
        repositioned_corners (list of np.ndarray): QR corners repositioned around hex center
    """
    # Ensure corners is a list of [x, y] pairs
    corners = np.squeeze(np.array(corners)).tolist()

    qr_size, angle_rad, tile_rot_deg, qr_origin = normalize_square(corners)

    offset = [0, -qr_size * 0.66]
    rotated_offset = rotate_offset(offset, -angle_rad)

    hex_center = np.array(qr_origin) + rotated_offset

    return tile_rot_deg, tuple(hex_center)
    
def scan_image(path, tile_metadata=None):
    """
    Scans an image for QR codes and returns Tile objects with metadata and layout geometry.

    Parameters:
        path (str): Path to the image file.
        icon_lookup (dict, optional): A dictionary mapping QR IDs to metadata (e.g., icon).

    Returns:
        img (np.ndarray): The original image.
        tiles (List[Tile]): List of Tile objects with detected positions and metadata.
        hex_diag (float): Estimated hexagon height based on QR size.
        hex_width (float): Estimated hexagon width based on QR size.
    """
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Image not found or couldn't be read: {path}")

    detector = cv2.QRCodeDetector()
    detector.setEpsX(0.1)
    detector.setEpsY(0.1)

    # Pre-process the image before decoding
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Use the thresholded image for detection
    ok, decoded, points, _ = detector.detectAndDecodeMulti(gray)

    qr_size = None

    tiles = []
    if ok:
        for data, corners in zip(decoded, points):
            if data.strip() == "":
                continue
            # print("Tile:", data)
                    # --- Normalize corner structure ---

            corners = np.squeeze(corners)
            if corners.shape != (4, 2):
                # print(f"Skipping malformed corners for {data}: shape={corners.shape}")
                continue
            corners = corners.tolist()  # Now guaranteed to be List[List[x, y]]

            if qr_size is None:
                qr_size = calculate_square_side(corners)

            corners = np.squeeze(np.array(corners)).tolist()
            
            tile_rot_deg, hex_center = regulate_tile(corners)
            centroid = tuple(float(x) for x in hex_center)

            attributes = tile_metadata.get(data, {}) if tile_metadata else {}
            tile = create_tile(qr_id=data, centroid=centroid, attributes=attributes)
            tile.attributes["rotation"] = tile_rot_deg
            tile.attributes["og_corners"] = corners
            tiles.append(tile)
    

    # change if the ratio if the QR OR physical hex tile changes, disproportionate to eachother
    hex_width = qr_size * 2.66 if qr_size else 0
    # print("hex_width: ", hex_width)

    return img, tiles, hex_width
