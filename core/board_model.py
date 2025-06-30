import json
import os
from core.tile_model import Tile, ObjectTile, AnchorTile

zone_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "zone_shapes.json")
with open(zone_path) as f:
    zone_shapes = json.load(f)

ZONE_OFFSETS = zone_shapes["hex"]


def analyze_cross_zone_neighbors(anchor_tiles, object_tiles, adjacency_map):
    # Build reverse mapping from tile ID → zone (anchor) ID
    tile_to_zone = {}
    for anchor_id, anchor_tile in anchor_tiles.items():
        for child_id in anchor_tile.children:
            tile_to_zone[child_id] = anchor_id

    cross_zone_relations = []

    for tile_id, neighbors in adjacency_map.items():
        tile_zone = tile_to_zone.get(tile_id)

        for neighbor_id in neighbors:
            if neighbor_id not in object_tiles:
                continue  # skip if neighbor is an anchor or missing

            neighbor_zone = tile_to_zone.get(neighbor_id)

            if tile_zone and neighbor_zone:
                if tile_zone != neighbor_zone:
                    cross_zone_relations.append({
                        "tile_id": tile_id,
                        "neighbor_id": neighbor_id,
                        "tile_zone": tile_zone,
                        "neighbor_zone": neighbor_zone,
                        "type": "cross-zone"
                    })
            elif tile_zone and not neighbor_zone:
                cross_zone_relations.append({
                    "tile_id": tile_id,
                    "neighbor_id": neighbor_id,
                    "tile_zone": tile_zone,
                    "neighbor_zone": None,
                    "type": "unassigned-neighbor"
                })
            elif not tile_zone and neighbor_zone:
                cross_zone_relations.append({
                    "tile_id": tile_id,
                    "neighbor_id": neighbor_id,
                    "tile_zone": None,
                    "neighbor_zone": neighbor_zone,
                    "type": "unassigned-neighbor"
                })

    return cross_zone_relations



class BoardModel:
    def __init__(self, tiles: list[Tile], hex_width: float):
        self.tiles = tiles
        self.hex_width = hex_width
        self.object_tiles = {t.qr_id: t for t in tiles if isinstance(t, ObjectTile)}
        self.anchor_tiles = {t.qr_id: t for t in tiles if isinstance(t, AnchorTile)}
        self.axial_map = {}

        # if __debug__: 
        #     for tile in self.tiles:
        #         print(f"{tile.qr_id}: centroid={tile.centroid}")
        #         print(f"axial={self.centroid_to_axial(tile.centroid, self.hex_width)}")

        # for tile in self.tiles:
        #     axial = self.centroid_to_axial(tile.centroid, self.hex_width)
        #     self.axial_map[tile.qr_id] = axial

        # if __debug__: 
        #     print("Axial Map:")
        #     for tid, coords in self.axial_map.items():
        #         print(f"{tid}: {coords}")

        # if __debug__: 
        #     # Compare anchor to all object tiles
        #     test_anchor = "id_027"
        #     for tid, coords in self.axial_map.items():
        #         if tid != test_anchor:
        #             aq, ar = self.axial_map[test_anchor]
        #             tq, tr = coords
        #             delta = (tq - aq, tr - ar)
        #             if delta in ZONE_OFFSETS:
        #                 print(f"✓ {tid} is adjacent to {test_anchor} with delta {delta}")
        #             else:
        #                 print(f"✗ {tid} is NOT adjacent to {test_anchor} (delta {delta})")
        #         else:
        #             print(f"[DEBUG] Anchor {test_anchor} not found in axial map.")
                        
        self.adjacency_map = self.build_adjacency_map()
        
        # if __debug__: 
        #     print("Adjacency for anchors:")
        #     for aid in self.anchor_tiles:
        #         print(f"{aid}: {self.adjacency_map.get(aid)}")

        self.assign_zones() # assign anchors to children, children to anchors


    def hex_round(q, r):
        """
        Rounds axial (q, r) coordinates to the nearest valid hex tile center.

        Rounding ensures the coordinates preserve q + r + s = 0.

        Parameters:
            q (float): q axial coordinate (horizontal component)
            r (float): r axial coordinate (diagonal or vertical component)

        Returns:
            tuple[int, int]: rounded axial coordinates (q, r) corresponding to the nearest hex center.
        """
        s = -q - r
        rq, rr, rs = round(q), round(r), round(s)

        dq, dr, ds = abs(rq - q), abs(rr - r), abs(rs - s)
        if dq > dr and dq > ds:
            rq = -rr - rs
        elif dr > ds:
            rr = -rq - rs
        else:
            rs = -rq - rr
        return (rq, rr)

    def axial_round(self, q, r):
        x = q
        z = r
        y = -x - z

        rx = round(x)
        ry = round(y)
        rz = round(z)

        x_diff = abs(rx - x)
        y_diff = abs(ry - y)
        z_diff = abs(rz - z)

        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        elif y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry

        return int(rx), int(rz)

    def centroid_to_axial(self, centroid, hex_width):
        x, y = centroid
        # size = hex_width / 2  # length from center to flat side
        size = hex_width / (3**0.5)  # use proper hex height-to-width scaling

        q = (x * (2/3)) / size
        r = (-x / 3 + (3**0.5 / 3) * y) / size
        
        return self.axial_round(q, r)

    def build_adjacency_map(self):
        """
        Constructs a spatial adjacency map for tiles based on their centroid positions.

        Parameters:
            tiles (list of Tile): The scanned tile objects.
            hex_width (float): Expected center-to-center spacing between hex tiles.
            margin (float): Additional margin percentage to account for minor variation.

        Returns:
            dict: Mapping of tile IDs to lists of adjacent tile IDs.
        """
        self.axial_map = {}
        for tile in self.tiles:
            self.axial_map[tile.qr_id] = self.centroid_to_axial(tile.centroid, self.hex_width)

        # print(ZONE_OFFSETS)

        adjacency_map = {}
        axial_to_id = {coords: qr_id for qr_id, coords in self.axial_map.items()}

        for qr_id, (q, r) in self.axial_map.items():
            neighbors = []
            for dq, dr in ZONE_OFFSETS:
                neighbor_coords = (q + dq, r + dr)
                neighbor_id = axial_to_id.get(neighbor_coords)
                if neighbor_id:
                    neighbors.append(neighbor_id)
            adjacency_map[qr_id] = neighbors


        return adjacency_map


    def assign_zones(self):
        # print("should assign zones")
        anchors = {tile.qr_id: tile for tile in self.tiles if isinstance(tile, AnchorTile)}
        objects = {tile.qr_id: tile for tile in self.tiles if isinstance(tile, ObjectTile)}

        for anchor_id, anchor_tile in anchors.items():
            neighbors = self.adjacency_map.get(anchor_id, [])
            for neighbor_id in neighbors:
                if neighbor_id in objects:
                    obj_tile = objects[neighbor_id]
                    if obj_tile.assigned_to is None:  # Prevent double assignment
                        obj_tile.assigned_to = anchor_id
                        anchor_tile.add_child(obj_tile)
                        # print("anchor", anchor_tile, " child: ", obj_tile)

        return self.object_tiles, self.anchor_tiles, self.hex_width

    def get_unassigned_neighbors_of_children(self, anchor_tile):
        tile_lookup = {tile.qr_id: tile for tile in self.tiles}
        potential_siblings = set()

        for child_id in anchor_tile.children:
            neighbors = self.adjacency_map.get(child_id, [])
            for neighbor_id in neighbors:
                if neighbor_id not in anchor_tile.children:
                    neighbor_tile = tile_lookup.get(neighbor_id)
                    if isinstance(neighbor_tile, ObjectTile):
                        potential_siblings.add(neighbor_id)

        return list(potential_siblings)

    def analyze_cross_zone_neighbors(self):
        """
        Returns:
        [
            {
                "tile_id": "id_002",
                "neighbor_id": "id_007",
                "tile_zone": "id_010",
                "neighbor_zone": "id_011",
                "type": "cross-zone"
            },
            ...
        ]
        """
        return self.anchor_tiles, self.object_tiles, self.adjacency_map


    def get_tile_by_id(self, tile_id):
        return next((t for t in self.tiles if t.qr_id == tile_id), None)

    def get_anchors_of_tile(self, tile):
        """
        Returns a list of AnchorTile(s) associated with a given tile.

        - If the tile *is* an AnchorTile, return it as a single-item list.
        - If the tile is assigned to one or more anchors, return the list of matching AnchorTile objects.
        - If no matching anchors are found, return an empty list.
        """
        if isinstance(tile, AnchorTile):
            return [tile]
        
        assigned = tile.assigned_to
        if isinstance(assigned, list):
            return [self.anchor_tiles[aid] for aid in assigned if aid in self.anchor_tiles]
        elif assigned in self.anchor_tiles:
            return [self.anchor_tiles[assigned]]
        
        return []


    def print_adjacency_map(self):
        # print("\nAdjacency Map:")
        if not self.adjacency_map:
            print("Adjacency map is empty or not yet initialized.")
            return

        for tile_id, neighbors in self.adjacency_map.items():
            print(f"{tile_id}: {neighbors}")

    def get_tile_neighbors_by_id(self, tile_id: str) -> list:
        """
        Returns a list of neighbor tile IDs for a given tile ID.

        Parameters:
            tile_id (str): The QR ID of the tile whose neighbors you want.

        Returns:
            list: A list of QR IDs of adjacent tiles, or an empty list if not found.
        """
        if self.adjacency_map is None:
            raise ValueError("Adjacency map has not been built yet.")
        return self.adjacency_map.get(tile_id, [])