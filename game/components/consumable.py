from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from game.actions import Action, ItemAction
from game.color import health_recovered
from game.components.base_component import BaseComponent
from game.exceptions import Impossible
import game.entity


class Consumable(BaseComponent):
    parent: game.entity.Item

    def get_action(self, consumer: game.entity.Actor) -> Optional[Action]:
        """Try to return the action for this item."""
        return ItemAction(consumer, self.parent)

    def activate(self, action: ItemAction) -> None:
        """Invoke this items ability.

        `action` is the context for this activation.
        """
        raise NotImplementedError()

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, game.components.inventory.Inventory):
            inventory.items.remove(entity)


class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: ItemAction) -> None:
        # Type check to ensure consumer is an Actor
        assert isinstance(action.entity, game.entity.Actor), "Consumer must be an Actor"
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} HP!",
                health_recovered,
            )
            self.consume()
        else:
            raise Impossible("Your health is already full.")
