from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Optional, Set

import numpy as np
import tcod

from game.entity import Actor
from game.tiles import SHROUD, wall

if TYPE_CHECKING:
    import game.engine
    import game.entity


class GameMap:
    def __init__(self, engine: game.engine.Engine, width: int, height: int):
        self.engine = engine
        self.width, self.height = width, height
        self.entities: Set[game.entity.Entity] = set()
        self.tiles = np.full((width, height), fill_value=wall, order="F")

        self.visible = np.full((width, height), fill_value=False, order="F")  # Tiles the player can currently see
        self.explored = np.full((width, height), fill_value=False, order="F")  # Tiles the player has seen before

    @property
    def gamemap(self) -> GameMap:
        """Part 8 refactoring prep: self reference for parent system"""
        return self

    @property
    def actors(self) -> Iterator[game.entity.Actor]:
        """Iterate over this maps living actors."""
        yield from (entity for entity in self.entities if isinstance(entity, Actor) and entity.is_alive)

    def get_blocking_entity_at_location(
        self,
        location_x: int,
        location_y: int,
    ) -> Optional[game.entity.Entity]:
        for entity in self.entities:
            if entity.blocks_movement and entity.x == location_x and entity.y == location_y:
                return entity

        return None

    def get_blocking_entity_at(self, x: int, y: int) -> Optional[game.entity.Entity]:
        """Alias for get_blocking_entity_at_location"""
        return self.get_blocking_entity_at_location(x, y)

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: tcod.console.Console) -> None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        console.rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=SHROUD,
        )

        entities_sorted_for_rendering = sorted(self.entities, key=lambda x: x.render_order.value)

        for entity in entities_sorted_for_rendering:
            # Only print entities that are in the FOV
            if self.visible[entity.x, entity.y]:
                console.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.color)
