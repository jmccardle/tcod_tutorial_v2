from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import game.engine
    import game.entity
    import game.game_map


class BaseComponent:
    parent: game.entity.Entity  # Owning entity instance.

    @property
    def gamemap(self) -> game.game_map.GameMap:
        gamemap = self.parent.gamemap
        assert gamemap is not None
        return gamemap

    @property
    def engine(self) -> game.engine.Engine:
        return self.gamemap.engine
