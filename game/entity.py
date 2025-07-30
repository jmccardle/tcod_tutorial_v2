from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING, Union

if TYPE_CHECKING:
    import game.game_map


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    # Part 8 refactoring prep: Will become Union[GameMap, Inventory] in Part 8
    gamemap: game.game_map.GameMap
    
    def __init__(
        self, 
        gamemap: Optional[game.game_map.GameMap] = None,
        x: int = 0, 
        y: int = 0, 
        char: str = "?", 
        color: Tuple[int, int, int] = (255, 255, 255)
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        if gamemap:
            # If gamemap isn't provided now then it will be set later.
            self.gamemap = gamemap
            gamemap.entities.add(self)

    def place(self, x: int, y: int, gamemap: Optional[game.game_map.GameMap] = None) -> None:
        """Place this entity at a new location. Handles moving across GameMaps."""
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "gamemap"):  # Possibly uninitialized.
                self.gamemap.entities.remove(self)
            self.gamemap = gamemap
            gamemap.entities.add(self)

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy