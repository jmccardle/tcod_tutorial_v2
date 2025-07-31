from __future__ import annotations

from typing import Optional, Tuple, Type, TYPE_CHECKING, Union

import game.render_order

if TYPE_CHECKING:
    import game.components.ai
    import game.components.fighter
    import game.game_map


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    # Part 8 refactoring prep: Will become Union[GameMap, Inventory] in Part 8
    gamemap: Optional[game.game_map.GameMap]
    
    def __init__(
        self, 
        gamemap: Optional[game.game_map.GameMap] = None,
        x: int = 0, 
        y: int = 0, 
        char: str = "?", 
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        blocks_movement: bool = False,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = game.render_order.RenderOrder.CORPSE
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


class Actor(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        ai_cls: Type[game.components.ai.BaseAI],
        fighter: game.components.fighter.Fighter
    ):
        super().__init__(
            gamemap=None,
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
        )
        
        self.ai: Optional[game.components.ai.BaseAI] = ai_cls(self) if ai_cls else None
        
        self.fighter = fighter
        self.fighter.parent = self
        
        self.render_order = game.render_order.RenderOrder.ACTOR

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)