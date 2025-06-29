from PyQt6.QtWidgets import QGraphicsView, QGraphicsItem, QGraphicsTextItem
from PyQt6.QtGui import QBrush, QPen, QColor, QPainterPath, QPainter, QAction
from PyQt6.QtCore import QRectF, QPointF, Qt, pyqtSignal
import math
from core.tile_model import Tile, AnchorTile, ObjectTile
from gui.custom_board_scene import CustomBoardScene

# Constants for rendering
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
    tile_selected = pyqtSignal(Tile) #emits Tile object

    def __init__(self, board, tile_attributes, color_map, parent=None):
        super().__init__(parent)
        self.tile_items = []
        self.setScene(CustomBoardScene())
        # self.setScene(self.scene)
        self.scene().tile_selected.connect(self.tile_selected.emit) #scene.tile_selected → board_view.tile_selected → tile_sidebar.select_item_by_id

        self.board = board
        self.tile_attributes = tile_attributes
        self.color_map = color_map
        self.axial_coords = self.set_axial_coords()
        self.rendered_hex_size = self.calculate_rendered_hex_size()
        # print(self.rendered_hex_size)

        self.render_board()
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        # cap zooming
        self.current_scale = 1.0
        self.max_scale = 3.0
        self.min_scale = 0.5
        
        self.highlighted_item = None  # store the last tile item selected by user

    def set_axial_coords(self):
        """
        Returns a dictionary mapping tile IDs to their axial (q, r) coordinates,
        based on the BoardModel's axial_map.
        """
        coords = {}
        for tile in self.board.tiles:
            axial = self.board.axial_map.get(tile.qr_id)
            if axial is not None:
                coords[tile.qr_id] = axial
        return coords

    def render_board(self):
        """
        Populates the graphics scene with tile items positioned using axial coordinates.
        """
        self.tile_items = []  # Track all tile graphics items

        for tile in self.board.tiles:
            q, r = self.axial_coords.get(tile.qr_id, (0, 0))  # Safe fallback
            x, y = axial_to_pixel(q, r, self.rendered_hex_size)
            color = self.resolve_tile_color(tile.qr_id)

            tile_item = TileGraphicsItem(tile, color, self.rendered_hex_size)
            tile_item.setPos(QPointF(x, y))

            # Optional: let tile_item know its parent view for emitting signals if needed
            tile_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

            self.scene().addItem(tile_item)
            self.tile_items.append(tile_item)


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


    def calculate_rendered_hex_size(self):
        """
        Sets the rendered hex size so all tiles fit within the current view.
        """
        if not self.axial_coords:
            return

        qs = [q for q, _ in self.axial_coords.values()]
        rs = [r for _, r in self.axial_coords.values()]
        
        min_q, max_q = min(qs), max(qs)
        min_r, max_r = min(rs), max(rs)

        board_width = max_q - min_q + 1
        board_height = max_r - min_r + 1

        view_width = self.viewport().width()
        view_height = self.viewport().height()

        # Estimate hex size so they fit in view
        size_x = view_width / (board_width * 1.5 + 0.5)
        size_y = view_height / ((board_height + 0.5) * (3**0.5))

        return min(size_x, size_y)
    
    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0 and self.current_scale < self.max_scale:
            factor = zoom_in_factor
        elif event.angleDelta().y() < 0 and self.current_scale > self.min_scale:
            factor = zoom_out_factor
        else:
            return  # out of bounds

        self.current_scale *= factor
        self.scale(factor, factor)
    
    def highlight_tile_by_id(self, tile_id: str):
        # print(f"[DEBUG] highlight_tile_by_id: {tile_id}")
        for item in self.tile_items:
            item.highlighted = (item.tile.qr_id == tile_id)
            item.update()

    # def handle_tile_selected(self, tile: Tile):
    #     print(f"[DEBUG] handle_tile_selected: {tile.qr_id}")
    #     # for item in self.scene.items():
    #     for item in self.scene().items():
    #         if isinstance(item, TileGraphicsItem):
    #             item.set_highlight(item.tile.qr_id == tile.qr_id)

    def handle_tile_selected(self, tile):
        # print(f"[DEBUG] handle_tile_selected: {tile.qr_id}")
        self.highlight_tile_by_id(tile.qr_id)

    def on_tile_clicked(self, tile: Tile):  # now receives the full Tile
        # print(f"[DEBUG] on_tile_selected: {tile.qr_id}")
        self.highlight_tile_by_id(tile.qr_id)
        self.tile_selected.emit(tile)  # emit Tile object instead of ID


def axial_to_pixel(q, r, rendered_hex_size):
    """
    Converts axial coordinates to pixel position for flat-topped hexagons.

    Parameters:
        q (int): Axial column
        r (int): Axial row
        hex_size (float): Length from center to flat side (radius)

    Returns:
        (float, float): x, y position in pixels
    """
    width = 2 * rendered_hex_size
    height = math.sqrt(3) * rendered_hex_size  # vertical height of hex

    x = width * (3/4) * q
    y = height * (r + q / 2)

    return x, y



class TileGraphicsItem(QGraphicsItem):
    """
    A custom QGraphicsItem that represents a hexagonal tile.

    Parameters:
        tile (Tile): The tile object containing display data.
        color (QColor): Fill color for the tile.
        size (float): Radius of the hexagon from center to vertex.
    """
    tile_clicked = pyqtSignal(Tile)  # Emits qr_id
    
    def __init__(self, tile, color, size):
        super().__init__()
        self.tile = tile
        self.color = color
        self.size = size
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

        # Add label text to the center of the tile
        self.label_item = QGraphicsTextItem(tile.icon(), self)
        self.label_item.setDefaultTextColor(QColor("black"))

        bounds = self.label_item.boundingRect()
        self.label_item.setTransformOriginPoint(bounds.center())

        # Position the label so its center aligns with the tile's center
        self.label_item.setPos(-bounds.width() / 2, -bounds.height() / 2)

        # Rotate to match tile
        rotation_deg = self.tile.attributes.get("rotation", 0)
        self.label_item.setRotation(rotation_deg)

        self.highlighted = False
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        

    def boundingRect(self):
        """
        Returns the bounding rectangle for the tile item.

        Returns:
            QRectF: The bounding rectangle.
        """
        return QRectF(-self.size, -self.size, 2 * self.size, 2 * self.size)

    def set_highlight(self, state: bool):
        # print(f"[DEBUG] set_highlight: {self.tile.qr_id}")
        self.highlighted = state
        self.update()


    def paint(self, painter, option, widget):
        """
        Paints the hexagon shape and label for the tile.

        Parameters:
            painter (QPainter): The painter used to draw the item.
            option (QStyleOptionGraphicsItem): Style options.
            widget (QWidget): Optional widget reference.
        """
        points = self.create_hexagon_points()

        # Construct hexagon path
        path = QPainterPath()
        if points:
            path.moveTo(points[0])
            for point in points[1:]:
                path.lineTo(point)
            path.closeSubpath()

        # Fill
        painter.setBrush(QBrush(self.color))

        # Border priority: highlighted > anchor > none
        if self.highlighted:
            painter.setPen(QPen(QColor("red"), 3))
        elif isinstance(self.tile, AnchorTile):
            painter.setPen(QPen(ANCHOR_BORDER_COLOR, ANCHOR_BORDER_WIDTH))
        else:
            painter.setPen(QPen(Qt.PenStyle.NoPen))

        # Draw the hexagon
        painter.drawPath(path)

    def create_hexagon_points(self):
        rotation_deg = self.tile.attributes.get("rotation", 0)
        rotation_rad = math.radians(rotation_deg)

        points = []
        for i in range(6):
            angle_rad = math.radians(60 * i) + rotation_rad
            x = self.size * math.cos(angle_rad)
            y = self.size * math.sin(angle_rad)
            points.append(QPointF(x, y))
        return points
    
    def mousePressEvent(self, event):
        # print(f"[DEBUG] Tile on board clicked: {self.tile.qr_id}")
        scene = self.scene()
        if hasattr(scene, 'tile_was_clicked'):
            # print(f"[DEBUG] Calling tile_was_clicked for: {self.tile.qr_id}")
            scene.tile_was_clicked(self.tile)