from PyQt6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtCore import Qt, pyqtSignal
from core.tile_model import Tile, ObjectTile, AnchorTile
from gui.attribute_editor import AttributeEditor 


class TileSidebar(QWidget):
    """
    Widget  displays all known tiles in a vertical list.

    This sidebar allows users to:
    - View tile icons and basic status
    - Select a tile to view/edit its attributes
    - Synchronize selection with board view

    Emits:
        tile_selected (Tile): Signal emitted when a tile is selected from the sidebar.
    """
    tile_selected = pyqtSignal(Tile)

    def __init__(self, tile_data: dict, tiles: list[Tile], attribute_editor):
        """
        Initialize the TileSidebar widget.

        Parameters:
            tile_data (dict): A dictionary mapping tile IDs to attribute dictionaries.
            tiles (list[Tile]): A list of Tile objects currently scanned and tracked.
            attribute_editor (AttributeEditor): The attribute editor widget to update on selection.
        """
        super().__init__()

        self.tile_data = tile_data
        self.tiles = tiles
        self.attribute_editor = attribute_editor

        self.tile_list = QListWidget()
        self.tile_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)  # Optional: smoother scroll
        self.tile_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # Optional

        self.tile_list.itemClicked.connect(self.on_tile_clicked)

        self.populate_list()

        layout = QVBoxLayout()
        layout.addWidget(self.tile_list)
        self.setLayout(layout)

    def populate_list(self):
        """
        Populates the tile list, grouping tiles into two batches:
        1. Tiles currently on the board (have a matching Tile object)
        2. Tiles not yet scanned or placed on the board
        """
        self.tile_list.clear()

        on_board = []
        off_board = []

        tile_ids_on_board = {tile.qr_id for tile in self.tiles}

        for tile_id, attributes in self.tile_data.items():
            label = attributes.get("icon", tile_id)
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, tile_id)

            if tile_id in tile_ids_on_board:
                # Tile has been scanned/placed
                if len(attributes.keys()) > 1:
                    item.setBackground(QBrush(QColor("lightgreen")))  # tagged
                else:
                    item.setBackground(QBrush(QColor("khaki")))  # untagged
                on_board.append(item)
            else:
                # Tile not present on board
                item.setBackground(QBrush(QColor("lightgray")))
                off_board.append(item)

        for item in on_board + off_board:
            self.tile_list.addItem(item)

    def get_selected_tile_id(self):
        """
        Retrieves the currently selected tile ID from the list.

        Returns:
            str, None: The QR ID of the selected tile, or None if no selection.
        """
        item = self.tile_list.currentItem()
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def select_item_by_id(self, tile: Tile):
        """
        Programmatically selects a tile in the list by its QR ID.

        Parameters:
            tile (Tile): The tile object to select in the sidebar.
        """
        qr_id = tile.qr_id if isinstance(tile, Tile) else str(tile)
        for i in range(self.tile_list.count()):
            item = self.tile_list.item(i)
            item_id = item.data(Qt.ItemDataRole.UserRole)
            if item_id == qr_id:
                self.tile_list.setCurrentItem(item)
                item.setSelected(True)
                self.tile_list.scrollToItem(item)
                break

    def on_tile_clicked(self, item):
        tile_id = item.data(Qt.ItemDataRole.UserRole)

        # Clear highlights from all board tiles
        for tile in self.tiles:
            if hasattr(tile, 'graphics_item'):
                tile.graphics_item.set_highlight(False)

        # Try to find the tile by ID
        tile = next((t for t in self.tiles if t.qr_id == tile_id), None)

        if tile:
            if hasattr(tile, 'graphics_item'):
                tile.graphics_item.set_highlight(True)
        else:
            # Make a dummy Tile if not scanned (still allow attribute editing)
            tile = Tile(qr_id=tile_id)

        # Update editor and emit
        self.tile_selected.emit(tile)
        self.attribute_editor.set_tile(tile)