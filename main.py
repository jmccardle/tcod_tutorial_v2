#!/usr/bin/env python3
import copy

import tcod

import game.engine
import game.entity_factories
import game.game_map
import game.input_handlers
import game.procgen


def main() -> None:
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 45

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 2

    tileset = tcod.tileset.load_tilesheet(
        "data/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    player = copy.deepcopy(game.entity_factories.player)
    
    engine = game.engine.Engine(player=player)

    engine.game_map = game.procgen.generate_dungeon(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        max_monsters_per_room=max_monsters_per_room,
        engine=engine,
    )
    engine.update_fov()
    
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