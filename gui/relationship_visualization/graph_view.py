from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import networkx as nx


class GraphViewTab(QWidget):
    def __init__(self, board):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.updateGeometry()

        self.set_graph(board)

        layout.addWidget(QLabel("Hierarchy Graph View"))
        layout.addWidget(self.canvas)


    def set_graph(self, board):
        self.board = board
        self.draw_graph()

    def draw_graph(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.clear()

        G = nx.Graph()
        adjacency_map = self.board.adjacency_map  # {tile_id: [neighbor_tile_ids]}
        tile_map = {t.qr_id: t for t in list(self.board.object_tiles.values()) + list(self.board.anchor_tiles.values())}

        for tile_id, neighbors in adjacency_map.items():
            G.add_node(tile_id)
            for n in neighbors:
                G.add_edge(tile_id, n)

        pos = nx.spring_layout(G)

        # Build label dictionary from tile.icon()
        labels = {}
        for tile_id in G.nodes():
            tile = tile_map.get(tile_id)
            labels[tile_id] = tile.icon() if tile else tile_id  # fallback to ID

        nx.draw(
            G, pos, ax=ax, with_labels=True, labels=labels,
            node_color='lightblue', edge_color='gray',
            node_size=1000, font_size=10
        )

        self.canvas.draw()
