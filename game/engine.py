from __future__ import annotations

from typing import TYPE_CHECKING

import tcod

import game.entity

if TYPE_CHECKING:
    import game.game_map


class Engine:
    game_map: game.game_map.GameMap
    
    def __init__(self, player: game.entity.Entity):
        self.player = player

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""
        self.game_map.visible[:] = tcod.map.compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
        )
        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.entities) - {self.player}:
            print(f'The {entity.name} wonders when it will get to take a real turn.')
    
    def render(self, console: tcod.console.Console) -> None:
        self.game_map.render(console)