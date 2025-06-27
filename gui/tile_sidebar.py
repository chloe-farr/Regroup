from PyQt6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtCore import Qt, pyqtSignal
from core.tile_model import Tile, ObjectTile, AnchorTile


class TileSidebar(QWidget):
    """
    Sidebar that displays a list of all known tiles from tile_attributes.json.

    Parameters:
        tile_attributes (dict): Mapping of tile ID to attribute dicts.
        scanned_tiles (set[str]): QR IDs of currently scanned tiles.
    """
    tile_selected = pyqtSignal(str)  # emits qr_id

    def __init__(self, tile_data: dict, tiles: list[Tile]):
        super().__init__()
        self.tile_data = tile_data  # merged static+dynamic attributes (from JSONs)
        self.tiles = tiles
        self.tile_list = QListWidget()
        # self.populate_list()
        self.init_ui()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tile_list)
        self.setLayout(self.layout)
        

    def populate_list(self):
        for tile_id, attrs in self.tile_data.items():
            icon = attrs.get("icon", "❓")
            item = QListWidgetItem(icon)

            # Determine visual indicator based on scanned + tag status
            if tile_id in self.tiles:
                if len(attrs.keys()) > 1:  # has tags besides 'icon'
                    item.setBackground(QBrush(QColor("lightgreen")))  # scanned + tagged
                else:
                    item.setBackground(QBrush(QColor("khaki")))  # scanned but no tags
            else:
                item.setBackground(QBrush(QColor("lightgray")))  # not scanned

            item.setData(Qt.ItemDataRole.UserRole, tile_id)
            self.tile_list.addItem(item)
        

    def get_selected_tile_id(self):
        """
        Returns the QR ID of the currently selected tile in the sidebar.
        """
        item = self.tile_list.currentItem()
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None
    

    def init_ui(self):
        layout = QVBoxLayout()

        for tile_id, attributes in self.tile_data.items():
            label = attributes.get("icon", tile_id)
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, tile_id)
            self.tile_list.addItem(item)

        # This must use self.tile_list, and tile_list must exist
        self.tile_list.itemClicked.connect(self.on_tile_clicked)

        layout.addWidget(self.tile_list)
        self.setLayout(layout)

    def on_tile_clicked(self, item):
        """
        When the user clicks a tile item in the sidebar
        """
        tile_id = item.data(Qt.ItemDataRole.UserRole)
        # print("[DEBUG] clicked tile",tile_id)
        self.tile_selected.emit(tile_id)

    def select_item_by_id(self, tile_id):
        # print(f"[DEBUG] Selecting in sidebar: {tile_id}")
        for i in range(self.tile_list.count()):
            item = self.tile_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == tile_id:
                self.tile_list.setCurrentItem(item)
                self.tile_list.scrollToItem(item)  # Ensure it's visible
                self.tile_list.setFocus(Qt.FocusReason.OtherFocusReason)  # Optional: give focus
                self.tile_selected.emit(tile_id)  # <-- manually emit the signal
                break