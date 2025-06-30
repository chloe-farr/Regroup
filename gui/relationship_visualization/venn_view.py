from matplotlib_venn import venn2, venn3
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from core.tile_model import AnchorTile, ObjectTile, Tile

class VennViewTab(QWidget):
    def __init__(self, board=None, parent=None):
        super().__init__(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.set_board(board)

    def set_board(self, board):
        self.board = board
        self.draw_venn()

    def draw_venn(self):
        if not self.board or not hasattr(self.board, 'adjacency_map'):
            print("No board or adjacency map found.")
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Collect anchor → set of icons mappings
        anchor_sets = {}

        icon_lookup = {}  # tile_id → icon
        for anchor in self.board.anchor_tiles.values():
            anchor_id = anchor.qr_id
            anchor_sets[anchor_id] = set()

        for obj in self.board.object_tiles.values():
            assigned = obj.assigned_to
            if assigned in anchor_sets:
                nickname = obj.attributes.get("nickname", "").strip()
                display_label = nickname if nickname else obj.icon()
                anchor_sets[assigned].add(display_label)

        print(f"anchor sets: {anchor_sets}")

        for tile in self.board.tiles:
            if isinstance(tile, ObjectTile) and hasattr(tile, "assigned_to"):
                print(f"object tile: {tile}")

                for anchor_id in tile.assigned_to:
                    if anchor_id in anchor_sets:

                        anchor_sets[anchor_id].add(tile.icon())

        anchors = list(anchor_sets.keys())
        
        sets = list(anchor_sets.values())


        # No anchors or empty sets
        if len(sets) == 0:
            ax.text(0.5, 0.5, "No anchors or sets to display", ha='center', va='center')
            self.canvas.draw()
            return

        labels = []
        colors = []
        for anchor_id in anchor_sets.keys():
            anchor = self.board.anchor_tiles[anchor_id]
            nickname = anchor.attributes.get("nickname", "").strip()
            label = nickname if nickname else anchor.icon()
            labels.append(label)


            # Get anchor color (fallback to gray if not set)
            color_name = anchor.attributes.get("color", "").strip().lower()
            if color_name in mcolors.CSS4_COLORS:
                colors.append(mcolors.CSS4_COLORS[color_name])
            else:
                colors.append("lightgray")

        venn_func = None
        
        # Handle 1, 2, or 3 sets
        if len(sets) == 1:
            only_label = icon_lookup.get(anchors[0], anchors[0])
            ax.set_title(f"Venn View – Anchor: {only_label}")
            for i, item in enumerate(sorted(sets[0])):
                ax.text(0.5, 0.9 - i * 0.1, item, ha='center')
            self.canvas.draw()
            return

        elif len(sets) == 2:
            print(f"Anchor sets being plotted:")
            for anchor_id, obj_ids in anchor_sets.items():
                print(f"  {anchor_id} → {obj_ids}")

            venn = venn2(subsets=sets, set_labels=labels, ax=ax, set_colors=colors)
        elif len(sets) == 3:
            venn = venn3(subsets=sets, set_labels=labels, ax=ax, set_colors=colors)
        else:
            ax.text(0.5, 0.5, "Only 2–3 anchors supported", ha='center', va='center')
            self.canvas.draw()
            return


        # Label the regions with tile icons
        regions = [
            ('10', sets[0] - sets[1]),
            ('01', sets[1] - sets[0]),
            ('11', sets[0] & sets[1])
        ]

        for region_code, values in regions:
            label = venn.get_label_by_id(region_code)
            if label:
                label.set_text("\n".join(sorted(values)))

        self.canvas.draw()