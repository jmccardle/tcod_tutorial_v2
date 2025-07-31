from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple, Type, Union

from game.render_order import RenderOrder

if TYPE_CHECKING:
    import game.components.ai
    import game.components.consumable
    import game.components.fighter
    import game.components.inventory

from game.game_map import GameMap


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    parent: Union[GameMap, game.components.inventory.Inventory]

    def __init__(
        self,
        parent: Optional[Union[GameMap, game.components.inventory.Inventory]] = None,
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
        self.render_order = RenderOrder.CORPSE
        if parent:
            # If parent isn't provided now then it will be set later.
            self.parent = parent
            if hasattr(parent, "entities"):
                parent.entities.add(self)

    @property
    def gamemap(self) -> GameMap:
        if isinstance(self.parent, GameMap):
            return self.parent
        else:
            return self.parent.gamemap

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        """Place this entity at a new location. Handles moving across GameMaps."""
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "parent"):  # Possibly uninitialized.
                if hasattr(self.parent, "entities"):
                    self.parent.entities.remove(self)
            self.parent = gamemap
            gamemap.entities.add(self)

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy

    def distance(self, x: int, y: int) -> float:
        """
        Return the distance between the current entity and the given (x, y) coordinate.
        """
        return float(((x - self.x) ** 2 + (y - self.y) ** 2) ** 0.5)


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
        fighter: game.components.fighter.Fighter,
        inventory: game.components.inventory.Inventory,
    ):
        super().__init__(
            parent=None,
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

        self.inventory = inventory
        self.inventory.parent = self

        self.render_order = RenderOrder.ACTOR

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)


class Item(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        consumable: Optional[game.components.consumable.Consumable] = None,
    ):
        super().__init__(
            parent=None,
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=False,
        )

        self.consumable = consumable

        if self.consumable:
            self.consumable.parent = self

        self.render_order = RenderOrder.ITEM
