from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Set

import numpy as np
import tcod

from game.tiles import floor, wall

if TYPE_CHECKING:
    import game.engine
    import game.entity


class GameMap:
    def __init__(self, engine: game.engine.Engine, width: int, height: int):
        self.engine = engine
        self.width, self.height = width, height
        self.entities: Set[game.entity.Entity] = set()
        self.tiles = np.full((width, height), fill_value=floor, order="F")

        # Create a simple test wall
        self.tiles[30:33, 22] = wall

    def get_blocking_entity_at_location(
        self,
        location_x: int,
        location_y: int,
    ) -> Optional[game.entity.Entity]:
        for entity in self.entities:
            if entity.x == location_x and entity.y == location_y:
                return entity

        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: tcod.console.Console) -> None:
        """
        Renders the map.

        For now, we'll render all tiles as visible.
        In Part 4 we'll add FOV.
        """
        console.rgb[0 : self.width, 0 : self.height] = self.tiles["light"]

        for entity in self.entities:
            console.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.color)
