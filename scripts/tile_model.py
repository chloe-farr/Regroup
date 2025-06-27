from dataclasses import dataclass, field
from typing import Tuple, Set, Dict, Any, Optional, Union


@dataclass
class Tile:
    """
    Abstract base class for all tile types.
    Common attributes such as QR ID, centroid position, and metadata.
    """
    qr_id: str
    centroid: Tuple[float, float] = (0.0, 0.0)
    attributes: Dict[str, Any] = field(default_factory=dict)

    def add_attr(self, key: str, value: Any):
        self.attributes[key] = value

    def add_attrs(self, new_attrs: Dict[str, Any]):
        self.attributes.update(new_attrs)

    def has_attr(self, key: str, value: Any = None) -> bool:
        if key not in self.attributes:
            return False
        return self.attributes[key] == value if value is not None else True

    def icon(self) -> str:
        return self.attributes.get("icon", "")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "qr_id": self.qr_id,
            "centroid": self.centroid,
            "attributes": dict(self.attributes),
            "type": self.__class__.__name__,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Tile':
        return create_tile(
            qr_id=data["qr_id"],
            centroid=tuple(data["centroid"]),
            attributes=data.get("attributes", {})
        )

@dataclass
class AnchorTile(Tile):
    """
    Represents a zone anchor tile that can group multiple object tiles.
    """
    children: Set[str] = field(default_factory=set)

    def add_child(self, tile: 'ObjectTile'):
        # print("adding tile.qr_id", {tile.qr_id}, " to: ", self.qr_id)
        self.children.add(tile.qr_id)
        tile.assigned_to = self.qr_id

    def __repr__(self):
        return f"<AnchorTile id={self.qr_id} icon='{self.icon()}' children={list(self.children)}>"    

@dataclass
class ObjectTile(Tile):
    """
    Represents a user-assignable object tile that belongs to an anchor.
    """
    assigned_to: Optional[str] = None
    
    def __repr__(self):
        anchor_id = self.assigned_to.qr_id if hasattr(self.assigned_to, 'qr_id') else self.assigned_to
        return f"<ObjectTile id={self.qr_id} icon='{self.icon()}' assigned_to={anchor_id}>"

def create_tile(qr_id: str, centroid: Tuple[float, float], attributes: Dict[str, Any]) -> Union[AnchorTile, ObjectTile]:
    """
    Factory function to create either an AnchorTile or ObjectTile instance based on attributes.

    Parameters:
        qr_id (str): Identifier extracted from the QR code.
        centroid (Tuple[float, float]): The (x, y) position of the tile's center.
        attributes (Dict[str, Any]): Metadata associated with the tile, typically including 'icon' and 'tile_type'.

    Returns:
        Union[AnchorTile, ObjectTile]: An instance of the appropriate tile subclass depending on the 'tile_type' field in attributes. 
            Defaults to ObjectTile if unspecified or unrecognized.
    """
    tile_type = attributes.get("tile_type")
    if tile_type == "anchor":
        return AnchorTile(qr_id=qr_id, centroid=centroid, attributes=attributes)
    else:
        return ObjectTile(qr_id=qr_id, centroid=centroid, attributes=attributes)
    

