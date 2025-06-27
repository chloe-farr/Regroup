from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtCore import pyqtSignal

class CustomBoardScene(QGraphicsScene):
    tile_selected = pyqtSignal(str)  # qr_id

    def tile_was_clicked(self, qr_id: str):
        print(f"[DEBUG] Emitting scene.tile_selected: {qr_id}")
        self.tile_selected.emit(qr_id)