from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.classes.entitylike import EntityLike
from draftsman.classes.entitylist import EntityList
from draftsman.classes.entity import Entity
from draftsman.classes.association import Association
from recipe import Recipe
from copy import deepcopy
from utils import *


class FactoryCellGroup(Group):
    def __init__(
        self, name="factory-cell", position=(0, 0), rel_pos=(0,0), recipe=EMPTY, **kwargs
    ):
        # type: (str, tuple, tuple, Recipe, **dict) -> None
        super(FactoryCellGroup, self).__init__(position=position, **kwargs)
        # self.id = id
        self.name = name
        if recipe is not EMPTY:
            self._type = recipe.item
        else:
            self._type = EMPTY
        self.position = position

        if rel_pos is not None:
            self.rel_pos = {"x": rel_pos["x"], "y": rel_pos["y"]}
        else:
            self.rel_pos = {"x": 0, "y": 0}

        # Optional to flip the group, but this may not be surported
        # by the annealer.  Could be something we try for a swap: a flip
        self.direction = Direction.NORTH
        if "direction" in kwargs:
            self.direction = kwargs["direction"]

    def updateNeighbours(self):
        # Iterate on entities
        entity: Entity
        for entity in self.entities:
            if entity.power_connectable:
                new_neighbours = []
                for idx in range(len(entity.neighbours)):
                    neighbour = entity.neighbours[idx]
                    na = Association(self.entities[neighbour().id])
                    entity.neighbours[idx] = na

    def updateConnections(self):
        self.find_entities_filtered
        entity: Entity
        for entity in self.entities:
            if entity.circuit_connectable:
                for side in entity.connections:
                    if side in {"1", "2"}:
                        for color in entity.connections[side]:
                            new_conn_data = []
                            for idx in range(len(entity.connections[side][color])):
                                point = entity.connections[side][color][idx]
                                connection = point["entity_id"]
                                na = Association(self.entities[connection().id])
                                entity.connections[side][color][idx]["entity_id"] = na
