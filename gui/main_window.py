from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QDockWidget
from gui.board_view import BoardView
from gui.tile_sidebar import TileSidebar
from PyQt6.QtCore import QRectF, QPointF, Qt, QTimer
from gui.scanned_board_view import ScannedBoardView
from core.board_scanner import cv2_to_pixmap  # wherever you put that function


class MainWindow(QMainWindow):
    """
    Main application window that hosts the board view and future GUI components.

    Parameters:
        board (Board): The logical board object with tile data and axial positions.
        tile_attributes (dict): Mapping of tile IDs to user-defined attributes.
        color_map (dict): Mapping of color names to hex values.
    """
    def __init__(self, board, tile_data, color_map, xray_img):
        super().__init__()
        self.setWindowTitle("Regroup")

        self.init_tile_sidebar(tile_data, board)
        self.init_board_view(board, tile_data, color_map)

        self.tile_sidebar.tile_selected.connect(self.board_view.handle_tile_selected)
        self.board_view.tile_selected.connect(self.tile_sidebar.select_item_by_id)

        self.init_scanned_board_view(xray_img)

        self.init_menu()


        QTimer.singleShot(0, self.defer_resize_docks) # allow user to resize widgets

    def init_tile_sidebar(self, tile_data, board):
        self.tile_sidebar = TileSidebar(tile_data, board.tiles)  # your existing QWidget subclass
        
        self.tile_menu_dock = QDockWidget("Tiles", self)
        self.tile_menu_dock.setWidget(self.tile_sidebar)

        # Allow user to hide, float, or resize the sidebar
        self.tile_menu_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.tile_menu_dock)

    def init_board_view(self, board, tile_data, color_map):
        # Create board view
        self.board_view = BoardView(board, tile_data, color_map)

        # Create a dockable widget for the board
        self.board_dock = QDockWidget("Board", self)
        self.board_dock.setWidget(self.board_view)

        # Enable resizing/floating/hiding for board dock
        self.board_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.setCentralWidget(self.board_view)
        # Add to main window, docked in center or another area
        # self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.board_dock)

    
    def init_scanned_board_view(self, xray_img):
        print("[DEBUG] Entering scanned board view init")
        self.xray_view = ScannedBoardView(xray_img)  # your existing QWidget subclass
        self.xray_dock = QDockWidget("Scanned Board", self)
        self.xray_dock.setWidget(self.xray_view)
        print("[DEBUG] xray dock widget set")

        self.xray_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.xray_dock)
        print("[DEBUG] xray_dock DockWidget added")

    def init_menu(self):
        view_menu = self.menuBar().addMenu("View")

        toggle_board = self.board_dock.toggleViewAction()
        toggle_sidebar = self.tile_menu_dock.toggleViewAction()
        toggle_xray = self.xray_dock.toggleViewAction()

        view_menu.addAction(toggle_board)
        view_menu.addAction(toggle_sidebar)
        view_menu.addAction(toggle_xray)

    def defer_resize_docks(self):
        self.resizeDocks(
            [self.tile_menu_dock, self.xray_dock],
            [self.width() * 0.25, self.width() * 0.25],
            Qt.Orientation.Horizontal
        )