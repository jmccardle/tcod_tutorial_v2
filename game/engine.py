from __future__ import annotations

from typing import TYPE_CHECKING
import lzma
import pickle

import tcod

import game.color
import game.entity
import game.message_log
import game.render_functions

if TYPE_CHECKING:
    import game.game_map


class Engine:
    game_map: game.game_map.GameMap
    game_world: game.game_map.GameWorld

    def __init__(self, player: game.entity.Actor):
        self.player = player
        self.mouse_location = (0, 0)
        self.message_log = game.message_log.MessageLog()

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

        game.render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
        )

        game.render_functions.render_dungeon_level(
            console=console,
            dungeon_level=self.game_world.current_floor,
            location=(0, 47),
        )

        console.print(
            x=0,
            y=46,
            string=f"LVL: {self.player.level.current_level}",
        )

        game.render_functions.render_names_at_mouse_location(console=console, x=21, y=44, engine=self)

    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)
