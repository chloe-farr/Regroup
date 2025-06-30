from PyQt6.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from .hierarchy_view import HierarchyViewTab #implement later
from .graph_view import GraphViewTab
from .venn_view import VennViewTab


class RelationshipVisualizationWidget(QWidget):
    """
    Dockable widget.
    Contains one tab per type of visualization
    """

    expandRequested = pyqtSignal()

    def __init__(self, board):
        super().__init__()
        tab_styles = """
            QTabBar::tab {
                background: #f0f0f0;
                color: #333;
                padding: 4px 8px;
                border: 1px solid #bbb;
                border-bottom: none;
                margin-right: 1px;
                font-weight: normal;
                border-radius: 4px 4px 0 0;
            }

            QTabBar::tab:selected {
                background: #ffffff;
                color: #000;
                font-weight: normal;
            }

            QTabWidget::pane {
                border: 1px solid #bbb;
                top: -1px;
            }

            QTabBar {
                alignment: left;
            }
        """
        self.board = board
        
        main_layout = QVBoxLayout()

        # Horizontal layout for tab bar + update button
        tabbar_layout = QHBoxLayout()
        self.tabs = QTabWidget()

        # Allow tab bar to expand, push button to right
        tabbar_layout.addWidget(self.tabs, stretch=1)

        # Create update button
        self.update_button = QPushButton("Update Visualizations")
        self.update_button.setFixedHeight(26)
        self.update_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_button.clicked.connect(self.refresh_all_tabs)
        tabbar_layout.addWidget(self.update_button, alignment=Qt.AlignmentFlag.AlignRight)

        # Add tabbar and button row to main layout
        main_layout.addLayout(tabbar_layout)

        # Set main layout
        self.setLayout(main_layout)

        # Tab for graph
        self.graph_view_tab = GraphViewTab(board)
        self.tabs.addTab(self.graph_view_tab, "Graph")
        self.graph_view_tab.setStyleSheet(tab_styles)

        # Tab for venn (temp graph to simulate multiple tabs)
        self.venn_view_tab = VennViewTab(board)
        self.tabs.addTab(self.venn_view_tab, "Venn")
        self.venn_view_tab.setStyleSheet(tab_styles)


        # Connect tab change to signal
        self.tabs.currentChanged.connect(lambda index: self.expandRequested.emit())

    def refresh_all_tabs(self):
        # Assumes each tab implements a `.draw_*()` method or `.set_board()` to redraw
        if hasattr(self.graph_view_tab, 'set_board'):
            self.graph_view_tab.set_board(self.board)
        if hasattr(self.venn_view_tab, 'set_board'):
            self.venn_view_tab.set_board(self.board)
        # if hasattr(self.tree_view_tab, 'set_board'):
        #     self.tree_view_tab.set_board(self.board)