from __future__ import annotations

from typing import TYPE_CHECKING

import game.components.base_component
import game.equipment_types

if TYPE_CHECKING:
    import game.entity


class Equippable(game.components.base_component.BaseComponent):
    parent: game.entity.Item

    def __init__(
        self,
        equipment_type: game.equipment_types.EquipmentType,
        power_bonus: int = 0,
        defense_bonus: int = 0,
    ):
        self.equipment_type = equipment_type

        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus


class Dagger(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=game.equipment_types.EquipmentType.WEAPON, power_bonus=2)


class Sword(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=game.equipment_types.EquipmentType.WEAPON, power_bonus=4)


class LeatherArmor(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=game.equipment_types.EquipmentType.ARMOR, defense_bonus=1)


class ChainMail(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=game.equipment_types.EquipmentType.ARMOR, defense_bonus=3)