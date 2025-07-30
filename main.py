#!/usr/bin/env python3
import tcod

import game.engine
import game.entity
import game.input_handlers


def main() -> None:
    screen_width = 80
    screen_height = 50

    tileset = tcod.tileset.load_tilesheet(
        "data/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    player = game.entity.Entity(
        x=int(screen_width / 2), y=int(screen_height / 2), char="@", color=(255, 255, 255)
    )

    engine = game.engine.Engine(player=player)
    
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