from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QDockWidget,QFileDialog, QApplication, QDialog
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtGui import QPainter, QAction
from PyQt6.QtCore import QRectF, QPointF, Qt, QTimer
from gui.board_view import BoardView
from gui.tile_sidebar import TileSidebar
from gui.scanned_board_view import ScannedBoardView
from gui.attribute_editor import AttributeEditor
from gui.relationship_visualization.visualization_widget import RelationshipVisualizationWidget
from core.board_scanner import cv2_to_pixmap
from core.camera_utils import capture_image

class MainWindow(QMainWindow):
    """
    Main application window that hosts the board view and future GUI components.

    Parameters:
        board (Board): The logical board object with tile data and axial positions.
        tile_attributes (dict): Mapping of tile IDs to user-defined attributes.
        color_map (dict): Mapping of color names to hex values.
    """
    def __init__(self, board, tile_data, color_map, xray_img, mock_board):
        super().__init__()
        self.mock_board = mock_board #allows function call in main.py during runtime.
        self.setWindowTitle("Regroup")

        self.init_attribute_editor(tile_data, board)
        self.init_tile_sidebar(tile_data, board, self.attribute_editor)
        
        self.init_board_view(board, tile_data, color_map)
        self.init_relationship_visualization_pane(board)

        self.tile_sidebar.tile_selected.connect(self.board_view.handle_tile_selected)
        self.tile_sidebar.tile_selected.connect(self.attribute_editor.set_tile)
        
        self.board_view.tile_selected.connect(self.tile_sidebar.select_item_by_id)
        self.board_view.tile_selected.connect(self.attribute_editor.set_tile)
        self.board_view.tile_selected.connect(self.board_view.handle_tile_selected)

        self.init_scanned_board_view(xray_img)

        self.init_menu()


        QTimer.singleShot(0, self.defer_resize_docks) # allow user to resize widgets
        self.showMaximized()

    def init_tile_sidebar(self, tile_data, board, attribute_editor):

        self.tile_sidebar = TileSidebar(tile_data, board.tiles, attribute_editor)  # your existing QWidget subclass

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
        # print("[DEBUG] Entering scanned board view init")
        self.xray_view = ScannedBoardView(xray_img)  # your existing QWidget subclass
        self.xray_dock = QDockWidget("Scanned Board", self)
        self.xray_dock.setWidget(self.xray_view)
        # print("[DEBUG] xray dock widget set")

        self.xray_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.xray_dock)
        # print("[DEBUG] xray_dock DockWidget added")


    def init_menu(self):
        menubar = self.menuBar()

        # ----- File Menu -----
        file_menu = menubar.addMenu("File")

        save_action = QAction("Save Attributes", self)
        save_action.triggered.connect(self.tile_sidebar.save_tile_data)
        file_menu.addAction(save_action)

        camera_action = QAction("Open Camera", self)
        camera_action.triggered.connect(self.open_camera_widget)
        file_menu.addAction(camera_action)

        # 'Export as PDF' submenu
        export_pdf_menu = file_menu.addMenu("Export as PDF")

        # Board export
        export_board_action = QAction("Board", self)
        export_board_action.triggered.connect(self.export_board_to_pdf)
        export_pdf_menu.addAction(export_board_action)

        # Relationships submenu
        relationships_menu = export_pdf_menu.addMenu("Relationships")

            # Venn export
        export_venn_action = QAction("Venn", self)
        export_venn_action.triggered.connect(lambda: self.export_visualization_pdf('venn'))
        relationships_menu.addAction(export_venn_action)

            # Graph export
        export_graph_action = QAction("Graph", self)
        export_graph_action.triggered.connect(lambda: self.export_visualization_pdf('graph'))
        relationships_menu.addAction(export_graph_action)

        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # ----- View Menu -----
        view_menu = menubar.addMenu("View")

        toggle_board = self.board_dock.toggleViewAction()
        toggle_sidebar = self.tile_menu_dock.toggleViewAction()
        toggle_xray = self.xray_dock.toggleViewAction()
        toggle_attribute_editor = self.attribute_dock.toggleViewAction()
        toggle_relationship_pane = self.relationship_dock.toggleViewAction()

        view_menu.addAction(toggle_board)
        view_menu.addAction(toggle_sidebar)
        view_menu.addAction(toggle_xray)
        view_menu.addAction(toggle_attribute_editor)
        view_menu.addAction(toggle_relationship_pane)

    def defer_resize_docks(self):
        self.resizeDocks(
            [self.tile_menu_dock, self.xray_dock],
            [self.width() * 0.25, self.width() * 0.25],
            Qt.Orientation.Horizontal
        )

    def export_board_to_pdf(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export to PDF", "", "PDF Files (*.pdf)")
        if not filename:
            return

        printer = QPrinter()
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(filename)

        painter = QPainter(printer)
        self.board_view.scene().render(painter)  # Optionally: pass QRect if you want clipping
        painter.end()
    
    
    def export_visualization_pdf(self, visualization_type):  # 'venn', 'graph'
        filename, _ = QFileDialog.getSaveFileName(self, "Export to PDF", f"{visualization_type}_output.pdf", "PDF Files (*.pdf)")
        if not filename:
            return

        printer = QPrinter()
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(filename)

        painter = QPainter()
        
        # Correct way to get the tab widget reference
        vis_tab = getattr(self.relationship_pane, f"{visualization_type}_view_tab", None)
        if vis_tab is None:
            print(f"Visualization tab '{visualization_type}_view_tab' not found.")
            return

        if not painter.begin(printer):
            print("Failed to open PDF for painting.")
            return

        vis_tab.render(painter)
        painter.end()


    def init_attribute_editor(self, tile_data, board):
        self.attribute_editor = AttributeEditor(tile_data, board)
        self.attribute_dock = QDockWidget("Attributes", self)
        self.attribute_dock.setWidget(self.attribute_editor)
        self.attribute_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.attribute_dock)

    def init_relationship_visualization_pane(self, board):
        self.relationship_dock = QDockWidget("Relationships", self)
        self.relationship_pane = RelationshipVisualizationWidget(board)
        self.relationship_dock.setWidget(self.relationship_pane)
        
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.relationship_dock) #dock to bottom
        self.relationship_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.relationship_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea) #restrict permitted docking area to bottom
        self.relationship_dock.setMinimumHeight(40)
        # self.relationship_dock.setMaximumHeight(70)

    def expand_relationship_dock(self):
        self.relationship_dock.setMaximumHeight(1000)  
        self.relationship_dock.setMinimumHeight(70)
        self.relationship_dock.setFixedHeight(self.height() * 0.25)

   
    def open_camera_widget(self):
        """
        This function currently doesn't work
        """
        # save tile data before scanning
        self.tile_sidebar.save_tile_data()

        # Capture image
        img = capture_image()

        if img is not None:
            try:
                new_board, new_tile_data = self.mock_board(img)
                self.board = new_board
                self.tile_sidebar.update_board(new_board, new_tile_data) #need to write update_board() in tile_sidebar.py
                
            except Exception as e:
                print(f"Failed to process image: {e}")