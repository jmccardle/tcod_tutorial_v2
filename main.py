#!/usr/bin/env python3
import tcod

from game.engine import Engine
from game.entity import Entity
from game.game_map import GameMap
from game.input_handlers import BaseEventHandler, MainGameEventHandler


def main() -> None:
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 45

    tileset = tcod.tileset.load_tilesheet("data/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD)

    engine = Engine(player=Entity())

    engine.game_map = GameMap(engine, map_width, map_height)

    # Create player and place in map
    engine.player.place(int(screen_width / 2), int(screen_height / 2), engine.game_map)
    engine.player.char = "@"
    engine.player.color = (255, 255, 255)

    # Create an NPC
    npc = Entity()
    npc.place(int(screen_width / 2 - 5), int(screen_height / 2), engine.game_map)
    npc.char = "@"
    npc.color = (255, 255, 0)

    # Part 10 refactoring: Track handler in main loop
    handler: BaseEventHandler = MainGameEventHandler(engine)

    with tcod.context.new(
        columns=screen_width,
        rows=screen_height,
        tileset=tileset,
        title="Yet Another Roguelike Tutorial",
        vsync=True,
    ) as context:
        root_console = tcod.console.Console(screen_width, screen_height, order="F")
        while True:
            root_console.clear()
            handler.on_render(console=root_console)
            context.present(root_console)

            # Part 10 refactoring: Handler manages its own state transitions
            for event in tcod.event.wait():
                handler = handler.handle_events(event)


if __name__ == "__main__":
    main()
