"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import copy
import lzma
import pickle
import traceback
from typing import Optional

from tcod import libtcodpy
import tcod

import game.color
import game.engine
import game.entity_factories
import game.game_map
import game.input_handlers
import game.procgen


# Load the background image and remove the alpha channel.
try:
    background_image = tcod.image.load("data/menu_background.png")[:, :, :3]
except FileNotFoundError:
    # Create a placeholder background if image is missing
    import numpy as np
    background_image = np.zeros((80, 50, 3), dtype=np.uint8)


def new_game() -> game.engine.Engine:
    """Return a brand new game session as an Engine instance."""
    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    max_monsters_per_room = 2
    max_items_per_room = 2

    player = copy.deepcopy(game.entity_factories.player)

    engine = game.engine.Engine(player=player)

    engine.game_map = game.procgen.generate_dungeon(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        max_monsters_per_room=max_monsters_per_room,
        max_items_per_room=max_items_per_room,
        engine=engine,
    )
    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, adventurer, to yet another dungeon!", game.color.welcome_text
    )
    return engine


def load_game(filename: str) -> game.engine.Engine:
    """Load an Engine instance from a file."""
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, game.engine.Engine)
    return engine


class MainMenu(game.input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input."""

    def on_render(self, console: tcod.console.Console) -> None:
        """Render the main menu on a background image."""
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "TOMBS OF THE ANCIENT KINGS",
            fg=game.color.menu_title,
            alignment=libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "By (Your name here)",
            fg=game.color.menu_title,
            alignment=libtcodpy.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(
            ["[N] Play a new game", "[C] Continue last game", "[Q] Quit"]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=game.color.menu_text,
                bg=game.color.black,
                alignment=libtcodpy.CENTER,
                bg_blend=libtcodpy.BKGND_ALPHA(64),
            )

    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[game.input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.KeySym.Q, tcod.event.KeySym.ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.KeySym.C:
            try:
                return game.input_handlers.MainGameEventHandler(load_game("savegame.sav"))
            except FileNotFoundError:
                return game.input_handlers.PopupMessage(self, "No saved game to load.")
            except Exception as exc:
                traceback.print_exc()  # Print to stderr.
                return game.input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.KeySym.N:
            return game.input_handlers.MainGameEventHandler(new_game())

        return None
