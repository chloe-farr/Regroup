# Regroup

## File Structure

regroup_app/
├── main.py                     # Scanned and interprets Tiles to Board based on QRs, Launches the GUI (creates MainWindow)
├── ui/
│   ├── main_window.py          # QMainWindow subclass — manages layout, top menu
│   ├── board_view.py           # QWidget or QGraphicsView for rendering the tile board
│   ├── tile_sidebar.py         # QWidget: tile list, show/hide, attribute triggers
│   ├── attribute_editor.py     # QWidget: shows attributes for selected tile, add/edit tags
│   ├── visualization_tabs.py   # QTabWidget: holds hierarchy/venn/buckets views
│   ├── photo_capture.py        # QWidget: opens camera via OpenCV, scans board
│   └── dialogs.py              # modal popups (e.g., print, export selection)
├── data/
│   ├── tile_definitions.json   # QR id to icon mappings (and immutable info)
│   ├── tile_attributes.json    # User-added attributes (persistent between scans)
│   └── scanned_board.json      # Optional exportable record of current board state
├── models/
│   ├── tile.py                 # Tile class with ID, position, icon, zone, attributes
│   ├── board.py                # Board class: manages tiles, adjacency, zones
│   └── scanner.py              # Core logic for interpreting QR data into tiles
├── controllers/
│   ├── board_controller.py     # Handles sync between scanned data and UI board
│   ├── attribute_controller.py # Loads/saves tile_attributes.json, syncs with sidebar
│   └── export_controller.py    # Handles printing, export image, save visualizations
└── assets/
    ├── icons/                  # Eye, info, plus, anchor radio icons
    ├── styles.qss              # Optional custom stylesheet
    └── fonts/

Basic features:
- QR scanning → tile object creation (DONE)
- Board rendering
- Full tile sidebar with dot indicators (scanned/annotated/etc.)
- Attribute editing pane (color + tags)
- Persistent attribute save/load
- Visual link between board and sidebar
- At least one working relational visualization view: buckets

Intermediate features:
- Fixed color dropdown UI (from pre-set color map)
- Tag suggestion dropdown or autocomplete
- Tab switch to visualization (e.g., dummy tab for now)
- Print/export board view
- Eye icon to toggle tile visibility
- Board zone highlighting (anchor group shading)


```
pip install networkx matplotlib pydot //in py env
brew install graphviz //in os
pip install matplotlib-venn
```