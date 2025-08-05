from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Iterator, Optional, Set

import numpy as np
import tcod

import game.tiles

if TYPE_CHECKING:
    import game.engine
    import game.entity


class GameMap:
    def __init__(
        self, engine: game.engine.Engine, width: int, height: int, entities: Iterable[game.entity.Entity] = ()
    ):
        self.engine = engine
        self.width, self.height = width, height
        self.entities: Set[game.entity.Entity] = set(entities)
        self.tiles = np.full((width, height), fill_value=game.tiles.wall, order="F")

        self.visible = np.full((width, height), fill_value=False, order="F")  # Tiles the player can currently see
        self.explored = np.full((width, height), fill_value=False, order="F")  # Tiles the player has seen before

        self.downstairs_location = (0, 0)

    @property
    def gamemap(self) -> GameMap:
        """Part 8 refactoring prep: self reference for parent system"""
        return self

    @property
    def actors(self) -> Iterator[game.entity.Actor]:
        """Iterate over this maps living actors."""
        yield from (entity for entity in self.entities if isinstance(entity, game.entity.Actor) and entity.is_alive)

    @property
    def items(self) -> Iterator[game.entity.Item]:
        yield from (entity for entity in self.entities if isinstance(entity, game.entity.Item))

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

    def get_actor_at_location(self, x: int, y: int) -> Optional[game.entity.Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

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
            default=game.tiles.SHROUD,
        )

        entities_sorted_for_rendering = sorted(self.entities, key=lambda x: x.render_order.value)

        for entity in entities_sorted_for_rendering:
            # Only print entities that are in the FOV
            if self.visible[entity.x, entity.y]:
                console.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.color)

        # Show stairs
        if self.visible[self.downstairs_location]:
            console.print(
                x=self.downstairs_location[0],
                y=self.downstairs_location[1],
                string=">",
                fg=(255, 255, 255),
            )


class GameWorld:
    """
    Holds the settings for the GameMap, and generates new maps when moving down the stairs.
    """

    def __init__(
        self,
        *,
        engine: game.engine.Engine,
        map_width: int,
        map_height: int,
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        current_floor: int = 0,
    ):
        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.current_floor = current_floor

    def generate_floor(self) -> None:
        from game.procgen import generate_dungeon

        self.current_floor += 1

        self.engine.game_map = generate_dungeon(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            current_floor=self.current_floor,
            engine=self.engine,
        )
