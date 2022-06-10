from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from globals import *

class FactoryCellGroup(Group):
    def __init__(
        self, 
        id, 
        name='factory-cell',
        position=(0,0),
        recipe=EMPTY,
        **kwargs
    ):
        super(FactoryCellGroup, self).__init__(id, position=position)
        self.id = id
        self.name = name
        self._type = recipe.item
        self.position = position

        self._tile_hashmap = SpatialHashMap()

        # Optional to flip the group, but this may not be surported
        # by the annealer.  Could be something we try for a swap: a flip
        self.direction = Direction.NORTH
        if "direction" in kwargs:
            self.direction = kwargs["direction"]

        