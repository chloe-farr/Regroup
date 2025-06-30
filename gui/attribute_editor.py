from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
    QLineEdit, QHBoxLayout, QComboBox, QFrame, QPushButton,QVBoxLayout
)
from core.tile_model import Tile, AnchorTile, ObjectTile
from core.board_model import BoardModel

class AttributeEditor(QWidget):
    def __init__(self, tile_data: dict, board: BoardModel):
        super().__init__()
        self.tile_data = tile_data
        self.board = board
        self.tile = None
        self.init_ui()

    def init_ui(self):
        self.label = QLabel("Attribute Editor")
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label)
        self.setLayout(main_layout)


    def set_tile(self, tile: Tile):
        self.tile = tile
        tile_attributes = tile.attributes
        self.clear_fields()

        # --- Header ---
        header = QLabel(f"Editing {tile.icon()}")
        self.layout().addWidget(header)

        # --- Common: Nickname ---
        self.nickname_field(tile_attributes)

        if isinstance(tile, ObjectTile):
            self.set_object_tile(tile)
        elif isinstance(tile, AnchorTile):
            self.set_anchor_tile(tile)

        self.add_new_attribute_ui(tile_attributes)

    def nickname_field(self, tile_attributes: dict):
        label = QLabel("Nickname:")
        edit = QLineEdit()
        edit.setText(tile_attributes.get("nickname", ""))
        edit.textChanged.connect(lambda text: tile_attributes.update({"nickname": text}))

        row = QHBoxLayout()
        row.addWidget(label)
        row.addWidget(edit)
        self.layout().addLayout(row)
        

    def set_object_tile(self, tile: ObjectTile):
        tile_attributes = tile.attributes

        # --- Zones (Uneditable) ---
        anchors = self.board.get_anchors_of_tile(tile)
        if anchors:
            zone_names = [f"{a.icon()} ({a.attributes.get('nickname', '')})" for a in anchors]
            zone_label = QLabel("Zone(s): " + ", ".join(zone_names))
        else:
            zone_label = QLabel("Zone: None")
        self.layout().addWidget(zone_label)

        # --- Editable Zone Name(s) ---
        for anchor in anchors:
            label = QLabel(f"Zone Name for {anchor.icon()}:")
            edit = QLineEdit()
            edit.setText(anchor.attributes.get("nickname", ""))

            # Bind the update to the correct anchor object
            edit.textChanged.connect(lambda text, a=anchor: a.attributes.update({"nickname": text}))

            row = QHBoxLayout()
            row.addWidget(label)
            row.addWidget(edit)
            self.layout().addLayout(row)

        # --- Placeholder: Siblings ---
        siblings_label = QLabel("Siblings: TBD")
        self.layout().addWidget(siblings_label)

        # --- Color Dropdown ---
        self.color_dropdown(tile_attributes)

        # --- Divider ---
        self.divider()

        # --- User Attributes ---
        self.user_defined_attributes(tile_attributes)


    def set_anchor_tile(self, tile: AnchorTile):
        tile_attributes = tile.attributes

        # --- Children (list ObjectTiles assigned to this anchor) ---
        children = [t for t in self.board.object_tiles.values() if t.assigned_to == tile.qr_id]
        child_names = ", ".join(t.icon() for t in children) if children else "None"
        children_label = QLabel(f"Children: {child_names}")
        self.layout().addWidget(children_label)

        # --- Color Dropdown ---
        self.color_dropdown(tile_attributes)

        # --- Divider ---
        self.divider()

        # --- User Attributes ---
        self.user_defined_attributes(tile_attributes)

        # --- Attribute Keys (Editable per anchor) ---
        attributes_label = QLabel("Attributes (for assigned tiles):")
        self.layout().addWidget(attributes_label)

        # Get or initialize the list of attribute keys
        existing_keys = tile_attributes.setdefault("attribute_keys", [])

        for key in existing_keys:
            key_row = QHBoxLayout()

            key_label = QLabel("Attribute:")
            key_edit = QLineEdit()
            key_edit.setText(key)

            def update_key(old_key=key):
                def handler(text):
                    try:
                        idx = tile_attributes["attribute_keys"].index(old_key)
                        tile_attributes["attribute_keys"][idx] = text
                    except ValueError:
                        pass  # silently ignore if old_key is no longer in the list
                return handler

            key_edit.textChanged.connect(update_key())

            key_row.addWidget(key_label)
            key_row.addWidget(key_edit)
            self.layout().addLayout(key_row)

        # --- Add Attribute Button ---
        add_key_button = QPushButton("Add Attribute")
        add_key_button.clicked.connect(lambda: self.add_attribute_key(tile))
        self.layout().addWidget(add_key_button)

    def add_attribute_key(self, anchor):
        anchor.attributes.setdefault("attribute_keys", []).append("new_key")
        self.set_tile(anchor)  # Re-render
        

    def color_dropdown(self, tile_attributes: dict):
        label = QLabel("Colour:")
        combo = QComboBox()
        combo.addItems(["None", "Red", "Blue", "Green", "Yellow"])
        current = tile_attributes.get("color", "None")
        index = combo.findText(current)
        if index != -1:
            combo.setCurrentIndex(index)
        combo.currentTextChanged.connect(lambda text: tile_attributes.update({"color": text}))

        row = QHBoxLayout()
        row.addWidget(label)
        row.addWidget(combo)
        self.layout().addLayout(row)

    def divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout().addWidget(line)

    def user_defined_attributes(self, tile_attributes: dict):
        system_keys = {"icon", "tile_type", "rotation", "og_corners", "qr_corners", "centroid"}

        for key, value in tile_attributes.items():
            if key in system_keys:
                continue  # Skip internal keys

            label = QLabel(f"{key}:")
            edit = QLineEdit(str(value))
            edit.textChanged.connect(lambda text, k=key: tile_attributes.update({k: text}))

            row = QHBoxLayout()
            row.addWidget(label)
            row.addWidget(edit)
            self.main_layout = QVBoxLayout()
            self.setLayout(self.main_layout)

    
    def add_new_attribute_ui(self, tile_attributes: dict):
        key_input = QLineEdit()
        key_input.setPlaceholderText("New attribute name")

        value_input = QLineEdit()
        value_input.setPlaceholderText("Value")

        add_button = QPushButton("Add")
        
        def add_attribute():
            key = key_input.text().strip()
            value = value_input.text().strip()
            if key and key not in tile_attributes:
                tile_attributes[key] = value

                # Add label and editable field to UI
                label = QLabel(f"{key}:")
                field = QLineEdit(value)
                field.textChanged.connect(lambda text, k=key: tile_attributes.update({k: text}))

                row = QHBoxLayout()
                row.addWidget(label)
                row.addWidget(field)
                self.layout.addLayout(row)

                # Clear input fields
                key_input.clear()
                value_input.clear()

        add_button.clicked.connect(add_attribute)

        input_row = QHBoxLayout()
        input_row.addWidget(key_input)
        input_row.addWidget(value_input)
        input_row.addWidget(add_button)

        self.layout().addLayout(input_row)

    def clear_fields(self):
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
            elif item.layout():
                self.clear_layout(item.layout())

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
            elif item.layout():
                self.clear_layout(item.layout())