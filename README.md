# Regroup

## File Structure

regroup_app/
├── main.py                     # Scanned and interprets Tiles to Board based on QRs, Launches the GUI (creates MainWindow)
├── gui/
│   ├── main_window.py          # QMainWindow subclass — manages layout, top menu
│   ├── board_view.py           # QWidget or QGraphicsView for rendering the tile board
│   ├── tile_sidebar.py         # QWidget: tile list, show/hide, attribute triggers
│   ├── attribute_editor.py     # QWidget: shows attributes for selected tile, add/edit tags
│   ├── relationship_visualization/ # contains scripts for each visualization tab
│   │   ├── graph_view.py       # QWidget: tab of visualization_Widget. Shows graph view of hexagon tile relationships 
│   │   ├── venn_view.py        # QWidget: tab of visualization_Widget. Shows Venn diagram of hexagon tile relationships 
│   │   ├── hierarchy_view.py   # Not implemented
│   │   ├── visualization_Widget.py   # QTabWidget: holds hierarchy/venn/buckets views
│   ├── photo_capture.py        # QWidget: opens camera via OpenCV, scans board - tested independent from app. Not integrated yet
│   └── dialogs.py              # modal popups (e.g., print, export selection)  - not implemented yet
├── data/
│   ├── tile_definitions.json   # QR id to icon mappings (and immutable info)
│   ├── tile_attributes.json    # User-added attributes (persistent between scans) - User can save. Overwrites app default on save. Need to implement user open/import
│   └── zone_shapes.json        # Axial positions for tiles around anchors
├── core/
│   ├── tile_model.py           # Tile class with ID, position, icon, zone, attributes
│   ├── board_model.py          # Board class: manages tiles, adjacency, zones
│   └── board_scanner.py        # Core logic for interpreting QR data into tiles
│   └── overlays.py             # opencv annotations for displaying QR processing
│   └── camera_utils.py         # Opens device camera to capture physical tiles
└── assets/
│    ├── imgs/                   # images scanned in by board_scanner to digitize
│   ├── styles.qss              # Custom stylesheet - not implemented
│   └── fonts/                  # Used by make_qr_segno.py
└── hardware_support_scripts/  
│   ├── make_qr_png.py          # Renders QR and label, saves to .png
│   ├── make_qr_segno.py        # Renders QR and label, saves to .svg


```
pip install networkx matplotlib pydot //in py env
brew install graphviz //in os
pip install matplotlib-venn
```