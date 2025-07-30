#!/usr/bin/env python3
import tcod

import game.engine
import game.entity
import game.game_map
import game.input_handlers


def main() -> None:
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 45

    tileset = tcod.tileset.load_tilesheet(
        "data/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    engine = game.engine.Engine(player=game.entity.Entity())

    engine.game_map = game.game_map.GameMap(engine, map_width, map_height)
    
    # Create player and place in map
    engine.player.place(int(screen_width / 2), int(screen_height / 2), engine.game_map)
    engine.player.char = "@"
    engine.player.color = (255, 255, 255)
    
    # Create an NPC
    npc = game.entity.Entity()
    npc.place(int(screen_width / 2 - 5), int(screen_height / 2), engine.game_map)
    npc.char = "@"
    npc.color = (255, 255, 0)
    
    # Part 10 refactoring: Track handler in main loop
    handler: game.input_handlers.BaseEventHandler = game.input_handlers.MainGameEventHandler(engine)

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