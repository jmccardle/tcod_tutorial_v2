from __future__ import annotations

from typing import TYPE_CHECKING, List

from game.components.base_component import BaseComponent

if TYPE_CHECKING:
    import game.entity
    import game.game_map


class Inventory(BaseComponent):
    parent: game.entity.Actor

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items: List[game.entity.Item] = []

    @property
    def gamemap(self) -> game.game_map.GameMap:
        return self.parent.gamemap

    def drop(self, item: game.entity.Item) -> None:
        """
        Removes an item from the inventory and restores it to the game map, at the player's current location.
        """
        self.items.remove(item)
        item.place(self.parent.x, self.parent.y, self.gamemap)

        self.engine.message_log.add_message(f"You dropped the {item.name}.")
