from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsTextItem
from PyQt6.QtGui import QBrush, QPen, QColor, QPainterPath, QPainter
from PyQt6.QtCore import QRectF, QPointF, Qt
import math
from core.tile_model import AnchorTile, ObjectTile


# Constants for rendering
HEX_SIZE = 50  # Radius from center to vertex of hexagon
DEFAULT_COLOR = QColor("lightgray")
ANCHOR_BORDER_COLOR = QColor("black")
ANCHOR_BORDER_WIDTH = 3

class BoardView(QGraphicsView):
    """
    A QGraphicsView that renders a hexagonal tile board using axial coordinates.

    Parameters:
        board (Board): The board object containing tile data and axial positions.
        tile_attributes (dict): Mapping of tile IDs to attribute dictionaries.
        color_map (dict): Mapping of color names to hex color codes.
        parent (QWidget): Optional parent widget.
    """
    def __init__(self, board, tile_attributes, color_map, parent=None):
        super().__init__(parent)
        self.board = board
        self.tile_attributes = tile_attributes
        self.color_map = color_map

        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.render_board()
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

    def render_board(self):
        """
        Populates the graphics scene with tile items positioned using axial coordinates.
        """
        for tile in self.board.tiles:
            axial_coords = self.board.axial_map.get(tile.qr_id)
            if axial_coords is None:
                continue  # Skip tiles with no axial position

            q, r = axial_coords
            x, y = axial_to_pixel(q, r, HEX_SIZE)
            color = self.resolve_tile_color(tile.qr_id)

            tile_item = TileGraphicsItem(tile, color, HEX_SIZE)
            tile_item.setPos(QPointF(x, y))
            self.scene.addItem(tile_item)

    def resolve_tile_color(self, qr_id):
        """
        Determines the fill color for a tile based on user-assigned attributes.

        Parameters:
            qr_id (str): The unique ID of the tile.

        Returns:
            QColor: The color to use for the tile.
        """
        attr = self.tile_attributes.get(qr_id, {})
        color_name = attr.get("color")
        if color_name and color_name in self.color_map:
            return QColor(self.color_map[color_name])
        return DEFAULT_COLOR


def axial_to_pixel(q, r, size):
    """
    Converts axial hex coordinates to pixel coordinates for rendering.

    Parameters:
        q (int): Axial q-coordinate.
        r (int): Axial r-coordinate.
        size (float): Size of the hexagon.

    Returns:
        tuple: (x, y) pixel coordinates.
    """
    x = size * (3 / 2 * q)
    y = size * (math.sqrt(3) * (r + q / 2))
    return x, y


class TileGraphicsItem(QGraphicsItem):
    """
    A custom QGraphicsItem that represents a hexagonal tile.

    Parameters:
        tile (Tile): The tile object containing display data.
        color (QColor): Fill color for the tile.
        size (float): Radius of the hexagon from center to vertex.
    """
    def __init__(self, tile, color, size):
        super().__init__()
        self.tile = tile
        self.color = color
        self.size = size
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # Add label text to the center of the tile
        self.label_item = QGraphicsTextItem(tile.icon(), self)
        self.label_item.setDefaultTextColor(QColor("black"))
        self.label_item.setPos(-10, -10)  # Adjust for rough centering

    def boundingRect(self):
        """
        Returns the bounding rectangle for the tile item.

        Returns:
            QRectF: The bounding rectangle.
        """
        return QRectF(-self.size, -self.size, 2 * self.size, 2 * self.size)

    def paint(self, painter, option, widget):
        """
        Paints the hexagon shape and label for the tile.

        Parameters:
            painter (QPainter): The painter used to draw the item.
            option (QStyleOptionGraphicsItem): Style options.
            widget (QWidget): Optional widget reference.
        """
        path = QPainterPath()
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.radians(angle_deg)
            x = self.size * math.cos(angle_rad)
            y = self.size * math.sin(angle_rad)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        path.closeSubpath()

        painter.setBrush(QBrush(self.color))
        # print(isinstance(self.tile, AnchorTile))
        if isinstance(self.tile, AnchorTile):
            painter.setPen(QPen(ANCHOR_BORDER_COLOR, ANCHOR_BORDER_WIDTH))
        else:
            painter.setPen(QPen(Qt.PenStyle.NoPen))

        painter.drawPath(path)