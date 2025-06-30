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
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.label)
        self.setLayout(self.main_layout)


    def set_tile(self, tile: Tile):
        self.tile = tile
        tile_attributes = tile.attributes
        self.clear_fields()

        # --- Header ---
        header = QLabel(f"Editing {tile.icon()}")
        self.main_layout.addWidget(header)

        # --- Common: Nickname ---
        self.nickname_field(tile_attributes)

        if isinstance(tile, ObjectTile):
            self.set_object_tile(tile)
        elif isinstance(tile, AnchorTile):
            self.set_anchor_tile(tile)

        if isinstance(tile, ObjectTile):
            self.add_new_attribute_ui(tile_attributes)
        
        self.user_defined_attributes(tile_attributes, tile)
        

    def nickname_field(self, tile_attributes: dict):
        label = QLabel("Nickname:")
        edit = QLineEdit()
        edit.setText(tile_attributes.get("nickname", ""))
        edit.textChanged.connect(lambda text: tile_attributes.update({"nickname": text}))

        row = QHBoxLayout()
        row.addWidget(label)
        row.addWidget(edit)

        container = QWidget()
        container.setLayout(row)
        self.main_layout.addWidget(container)        

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
        self.main_layout.addWidget(siblings_label)
        # --- Color Dropdown ---
        self.color_dropdown(tile_attributes)

        # --- Divider ---
        self.divider()

    def set_anchor_tile(self, tile: AnchorTile):
        tile_attributes = tile.attributes

        # --- Children (list ObjectTiles assigned to this anchor) ---
        children = [t for t in self.board.object_tiles.values() if t.assigned_to == tile.qr_id]
        child_names = ", ".join(t.icon() for t in children) if children else "None"
        children_label = QLabel(f"Children: {child_names}")
        self.main_layout.addWidget(children_label)
        # --- Color Dropdown ---
        self.color_dropdown(tile_attributes)

        # --- Divider ---
        self.divider()

        # --- Attribute Keys (Editable per anchor) ---
        attributes_label = QLabel("Attributes (for assigned tiles):")
        
        self.main_layout.addWidget(attributes_label)
         
        # Get or initialize the list of attribute keys
        existing_keys = tile_attributes.setdefault("attribute_keys", [])

        for i, key in enumerate(existing_keys):
            key_row = QHBoxLayout()

            key_label = QLabel("Attribute:")
            key_edit = QLineEdit()
            key_edit.setText(key)

            # Safer update using editingFinished
            def make_update_handler(index, line_edit):
                def handler():
                    new_text = line_edit.text().strip()
                    if new_text:
                        tile_attributes["attribute_keys"][index] = new_text
                return handler

            key_edit.editingFinished.connect(make_update_handler(i, key_edit))

            key_row.addWidget(key_label)
            key_row.addWidget(key_edit)
            self.layout().addLayout(key_row)

  
            container = QWidget()
            container.setLayout(key_row)
            self.main_layout.addWidget(container)

        # --- Add Attribute Button ---
        add_key_button = QPushButton("Add Attribute")
        add_key_button.clicked.connect(lambda: self.add_attribute_key(tile))
        add_key_button.clicked.connect(lambda: print("Add clicked"))
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

        container = QWidget()
        container.setLayout(row)
        self.main_layout.addWidget(container)  

    def divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.main_layout.addWidget(line)

    def user_defined_attributes(self, tile_attributes: dict, tile):
        system_keys = {"icon", "tile_type", "rotation", "og_corners", "qr_corners", "centroid"}
        
        for key, value in tile_attributes.items():
            if key in system_keys:
                continue  # Skip internal keys

            label = QLabel(f"{key}:")
            edit = QLineEdit(str(value))

            def make_updater(k):
                return lambda text: tile_attributes.update({k: text})

            edit.textChanged.connect(make_updater(key))

            row = QHBoxLayout()
            row.addWidget(label)
            row.addWidget(edit)        

            if isinstance(tile, ObjectTile): self.layout().addLayout(row) 

    
    def add_new_attribute_ui(self, tile_attributes: dict):
        if isinstance(self.tile, ObjectTile):
            anchors = self.board.get_anchors_of_tile(self.tile)
            key_input = QComboBox()
            key_input.setEditable(True)  # Allow user-defined text
            key_input.addItem("empty")
            for a in anchors:
                for key in a.attributes.get("attribute_keys", []):
                    key_input.addItem(key)
        else:
            key_input = QLineEdit()
            key_input.setPlaceholderText("New attribute name")

        value_input = QLineEdit()
        value_input.setPlaceholderText("Value")

        add_button = QPushButton("Add")

        def add_attribute():
            key = key_input.currentText().strip() if isinstance(key_input, QComboBox) else key_input.text().strip()
            value = value_input.text().strip()
            print(f"ADDING: {key=}, {value=}")  # Debug line

            if not key:
                return  # Do nothing on empty key

            if isinstance(self.tile, ObjectTile):
                tile_attributes[key] = value  # Always allow key update
            else:
                if key not in tile_attributes:
                    tile_attributes[key] = ""
                if key not in tile_attributes.get("attribute_keys", []):
                    tile_attributes.setdefault("attribute_keys", []).append(key)

            # Add label and editable field to UI
            label = QLabel(f"{key}:")
            field = QLineEdit(value)
            field.textChanged.connect(lambda text, k=key: tile_attributes.update({k: text}))

            row = QHBoxLayout()
            row.addWidget(label)
            row.addWidget(field)
            self.layout().addLayout(row)

            # Clear inputs
            if isinstance(key_input, QComboBox):
                key_input.setCurrentText("")
            else:
                key_input.clear()
            value_input.clear()

        add_button.clicked.connect(add_attribute)

        input_row = QHBoxLayout()
        input_row.addWidget(key_input)
        input_row.addWidget(value_input)
        input_row.addWidget(add_button)

        container = QWidget()
        container.setLayout(input_row)
        self.layout().addWidget(container)

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


    def add_attribute_row(self, key, value):
        tile_attributes = self.tile.attributes
        tile_attributes[key] = value

        label = QLabel(f"{key}:")
        field = QLineEdit(value)
        field.textChanged.connect(lambda text, k=key: tile_attributes.update({k: text}))

        row = QHBoxLayout()
        row.addWidget(label)
        row.addWidget(field)
        self.main_layout.addWidget(row)
