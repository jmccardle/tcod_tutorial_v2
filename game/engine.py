from __future__ import annotations

import tcod

import game.entity


class Engine:
    def __init__(self, player: game.entity.Entity):
        self.player = player

    def render(self, console: tcod.console.Console) -> None:
        console.print(x=self.player.x, y=self.player.y, string=self.player.char, fg=self.player.color)