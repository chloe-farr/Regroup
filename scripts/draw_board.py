import sys, math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene
)
from PyQt6.QtGui  import QPainter, QPolygonF
from PyQt6.QtCore import Qt, QSize, QPointF

# ─── stub so the example runs; replace with your real item ───────────
from PyQt6.QtWidgets import QGraphicsPolygonItem
class HexTileItem(QGraphicsPolygonItem):
    def __init__(self, tid: str, label: str, poly: QPolygonF):
        super().__init__(poly)
        self.setToolTip(f"{tid}: {label}")
# ──────────────────────────────────────────────────────────────────────

class HexBoardView(QGraphicsView):
    """
    A HexBoardView that scales its scene automatically
    """
    def __init__(self, all_tile_neighbours, tile_definitions, hex_size, parent=None):
        super().__init__(parent)

        self.hex_size         = hex_size
        self.tile_definitions = tile_definitions
        self.all_tile_neigh   = all_tile_neighbours

        scene = QGraphicsScene(self)          # one scene per view
        self.setScene(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        self.draw_board()

        # nice interactions ---------------------------------------------------
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor       (QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode           (QGraphicsView.DragMode.ScrollHandDrag)

    # ─────────────────────────────────────────────────────────────────────────
    # fit entire scene when view resizes
    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    # ─────────────────────────────────────────────────────────────────────────
    def draw_board(self):
        scene = self.scene()
        scene.clear()
        print("all neighbours map:", self.all_tile_neigh)

        # anchor = "id_006" if "id_006" in self.all_tile_neigh else next(iter(self.all_tile_neigh))
        # render_list = {anchor: (0, 0)} | self.all_tile_neigh[anchor]

        # Choose anchor tile
        anchor = "id_006" if "id_006" in self.all_tile_neigh else next(iter(self.all_tile_neigh))
        neighbour_map = self.all_tile_neigh[anchor]

        # Build render list: anchor + its neighbours with axial coords
        render_list = {anchor: (0, 0)}
        for offset, neighbor_tid in neighbour_map.items():  # FIXED: correct unpacking
            render_list[neighbor_tid] = offset

        # Now works perfectly:
        for tid, (q, r) in render_list.items():
        # for tid, coords in render_list.items():
            # q, r = coords[0] if isinstance(coords[0], (tuple, list)) else coords
            poly = self.hex_polygon(self.hex_size)
            x, y = self.axial_to_pixel(q, r, self.hex_size)
            item = HexTileItem(tid, self.tile_definitions.get(tid, {}).get("icon", "?"), poly)
            item.setPos(x, y)
            scene.addItem(item)

        self.centerOn(0, 0)

    # ─── helpers ────────────────────────────────────────────────────────────
    @staticmethod
    def axial_to_pixel(q, r, size):
        x = size * math.sqrt(3) * (q + r / 2)
        y = size * 1.5 * r
        return x, y

    @staticmethod
    def hex_polygon(size):
        pts = [QPointF(size * math.cos(math.radians(60*i - 30)),
                       size * math.sin(math.radians(60*i - 30)))
               for i in range(6)]
        return QPolygonF(pts)
    
class AspectRatioWindow(QMainWindow):
    """
    Locks the outer frame
    """
    def __init__(self, view: QGraphicsView, initial_size: tuple[int, int]):
        super().__init__()
        self._ratio = initial_size[0] / initial_size[1]
        self._guard = False                         # re-entry lock

        self.setCentralWidget(view)
        self.resize(*initial_size)
        self.setMinimumSize(QSize(200, 200))

    # ─── keep W:H constant no matter which edge is dragged ────────────────
    def resizeEvent(self, ev):
        if self._guard:
            return
        self._guard = True

        w, h = ev.size().width(), ev.size().height()
        if w / h > self._ratio:          # too wide → trim width
            w = int(h * self._ratio)
        else:                            # too tall → trim height
            h = int(w / self._ratio)

        super().resizeEvent(ev)
        self.resize(w, h)
        self._guard = False



def display_hex_board(all_neigh, tile_defs, canvas_size, hex_diag):
    """
    Top-level launcher
    """
    app = QApplication(sys.argv)

    # build the graphics view
    view = HexBoardView(all_neigh, tile_defs, hex_diag)

    # half-sized startup window keeping the original aspect ratio
    start_size = (canvas_size[0] // 2, canvas_size[1] // 2)
    win = AspectRatioWindow(view, start_size)
    win.setWindowTitle("Responsive, aspect-locked Hex Board")
    win.show()

    sys.exit(app.exec())