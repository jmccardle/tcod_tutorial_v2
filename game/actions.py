from __future__ import annotations

import game.engine
import game.entity


class Action:
    def __init__(self, entity: game.entity.Entity) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> game.engine.Engine:
        """Return the engine this action belongs to."""
        # In Part 1, we don't have gamemap yet, so we'll need a different approach
        # This will be refactored in Part 2 when we add GameMap
        raise NotImplementedError()

    def perform(self, engine: game.engine.Engine) -> None:
        """Perform this action with the objects needed to determine its scope.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self, engine: game.engine.Engine) -> None:
        raise SystemExit()


class ActionWithDirection(Action):
    def __init__(self, entity: game.entity.Entity, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    def perform(self, engine: game.engine.Engine) -> None:
        raise NotImplementedError()


class MovementAction(ActionWithDirection):
    def perform(self, engine: game.engine.Engine) -> None:
        dest_x = self.entity.x + self.dx
        dest_y = self.entity.y + self.dy

        # Check boundaries (hardcoded for Part 1, will be improved later)
        if 0 <= dest_x < 80 and 0 <= dest_y < 50:
            self.entity.move(self.dx, self.dy)