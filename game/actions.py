from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

from game.color import descend, enemy_atk, player_atk
from game.entity import Actor
from game.exceptions import Impossible

if TYPE_CHECKING:
    import game.components.inventory
    import game.engine
    import game.entity


class Action:
    def __init__(self, entity: game.entity.Entity) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> game.engine.Engine:
        """Return the engine this action belongs to."""
        assert self.entity.gamemap is not None, "Entity must be placed on a gamemap"
        return self.entity.gamemap.engine

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self) -> None:
        raise SystemExit()


class WaitAction(Action):
    def perform(self) -> None:
        pass


class ActionWithDirection(Action):
    def __init__(self, entity: game.entity.Entity, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[game.entity.Entity]:
        """Return the blocking entity at this actions destination."""
        return self.engine.game_map.get_blocking_entity_at(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[game.entity.Entity]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_blocking_entity_at(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()


class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            return  # No entity to attack.

        # Type checking to ensure both entities are Actors with fighter components
        assert isinstance(self.entity, Actor), "Attacker must be an Actor"
        assert isinstance(target, Actor), "Target must be an Actor"

        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_color = player_atk
        else:
            attack_color = enemy_atk

        if damage > 0:
            self.engine.message_log.add_message(f"{attack_desc} for {damage} hit points.", attack_color)
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(f"{attack_desc} but does no damage.", attack_color)


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            return  # Destination is out of bounds.
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            return  # Destination is blocked by a tile.
        if self.engine.game_map.get_blocking_entity_at(dest_x, dest_y):
            return  # Destination is blocked by an entity.

        self.entity.move(self.dx, self.dy)


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()


class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it."""

    def __init__(self, entity: game.entity.Actor):
        super().__init__(entity)

    def perform(self) -> None:
        # Type check to ensure entity is an Actor with inventory
        assert isinstance(self.entity, Actor), "Entity must be an Actor for inventory access"

        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise Impossible("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(f"You picked up the {item.name}!")
                return

        raise Impossible("There is nothing here to pick up.")


class ItemAction(Action):
    def __init__(self, entity: game.entity.Actor, item: game.entity.Item, target_xy: Optional[Tuple[int, int]] = None):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[game.entity.Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Invoke the items ability, this action will be given to provide context."""
        if self.item.consumable is not None:
            self.item.consumable.activate(self)
        else:
            raise Impossible("This item cannot be used.")


class DropItem(ItemAction):
    def perform(self) -> None:
        # Type check to ensure entity is an Actor with inventory
        assert isinstance(self.entity, Actor), "Entity must be an Actor for inventory access"
        self.entity.inventory.drop(self.item)


class TakeStairsAction(Action):
    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        if (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            self.engine.game_world.generate_floor()
            self.engine.message_log.add_message("You descend the staircase.", descend)
        else:
            raise game.exceptions.Impossible("There are no stairs here.")


class EquipAction(Action):
    def __init__(self, entity: game.entity.Actor, item: game.entity.Item):
        super().__init__(entity)

        self.item = item

    def perform(self) -> None:
        # Type check to ensure entity is an Actor with equipment
        assert isinstance(self.entity, game.entity.Actor), "Entity must be an Actor for equipment access"
        self.entity.equipment.toggle_equip(self.item)
