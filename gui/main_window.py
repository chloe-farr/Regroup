from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from gui.board_view import BoardView

class MainWindow(QMainWindow):
    """
    Main application window that hosts the board view and future GUI components.

    Parameters:
        board (Board): The logical board object with tile data and axial positions.
        tile_attributes (dict): Mapping of tile IDs to user-defined attributes.
        color_map (dict): Mapping of color names to hex values.
    """
    def __init__(self, board, tile_attributes, color_map, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Regroup")
        self.setGeometry(100, 100, 1200, 800)

        # Main layout container
        container = QWidget()
        layout = QVBoxLayout()

        # Create and add the board view
        self.board_view = BoardView(board, tile_attributes, color_map)
        layout.addWidget(self.board_view)

        container.setLayout(layout)
        self.setCentralWidget(container)
