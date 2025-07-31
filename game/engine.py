from __future__ import annotations

from typing import TYPE_CHECKING
import lzma
import pickle

import tcod

from game.color import welcome_text
from game.entity import Actor
from game.message_log import MessageLog
from game.render_functions import render_bar, render_names_at_mouse_location

if TYPE_CHECKING:
    import game.game_map


class Engine:
    game_map: game.game_map.GameMap

    def __init__(self, player: Actor):
        self.player = player
        self.mouse_location = (0, 0)
        self.message_log = MessageLog()

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
        for entity in self.game_map.actors:
            if entity is self.player:
                continue
            if entity.ai:
                entity.ai.perform()

    def render(self, console: tcod.console.Console) -> None:
        self.game_map.render(console)

        self.message_log.render(console=console, x=21, y=45, width=40, height=5)

        render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
        )

        render_names_at_mouse_location(console=console, x=21, y=44, engine=self)

    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)
