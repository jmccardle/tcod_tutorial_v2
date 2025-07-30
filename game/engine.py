from __future__ import annotations

from typing import TYPE_CHECKING

import tcod

from game.entity import Entity

if TYPE_CHECKING:
    import game.game_map


class Engine:
    game_map: game.game_map.GameMap

    def __init__(self, player: Entity):
        self.player = player

    def render(self, console: tcod.console.Console) -> None:
        self.game_map.render(console)
