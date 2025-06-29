from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtCore import pyqtSignal
from core.tile_model import Tile, ObjectTile, AnchorTile  # or wherever Tile is defined

class CustomBoardScene(QGraphicsScene):
    # tile_selected = pyqtSignal(str)  # qr_id
    tile_selected = pyqtSignal(Tile)

    # def tile_was_clicked(self, qr_id: str):
    #     print(f"[DEBUG] Emitting scene.tile_selected: {qr_id}")
    #     self.tile_selected.emit(qr_id)

    def tile_was_clicked(self, tile):
        print(f"[DEBUG] Emitting scene.tile_selected: {tile}")

        self.tile_selected.emit(tile)
        