from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.classes.entitylike import EntityLike
from draftsman.classes.entitylist import EntityList
from draftsman.classes.entity import Entity
from draftsman.classes.association import Association
from copy import deepcopy
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
        if(recipe is not EMPTY):
            self._type = recipe.item
        else:
            self._type = EMPTY
        self.position = position

        # Optional to flip the group, but this may not be surported
        # by the annealer.  Could be something we try for a swap: a flip
        self.direction = Direction.NORTH
        if "direction" in kwargs:
            self.direction = kwargs["direction"]

    @Group.entities.setter
    def entities(self, value):
        # type: (list[EntityLike]) -> None

        self._entity_hashmap.clear()

        if value is None:
            self._entities.clear()
        elif isinstance(value, list):
            self._entities = EntityList(self, value)
        elif isinstance(value, EntityList):
            # Just don't ask
            self._entities = deepcopy(value, memo={"new_parent": self})
        else:
            raise TypeError("'entities' must be an EntityList, list, or None")

        self.recalculate_area()
        # if(value is None):
        #     self._entity_hashmap.clear()
        #     self._entities.clear()
        # elif(isinstance(value, list) or isinstance(value, EntityList)):
        #     self._entity_hashmap.clear()
        #     self._entities = EntityList(self, value)
        # elif(isinstance(value, EntityList)):
        #     dpcopy = deepcopy(value)
        #     dpcopy._parent = self
        #     self._entities = dpcopy
        # elif(isinstance(value, list) or isinstance(value, EntityList)):
        #     self._entity_hashmap.clear()
        #     self._entities = EntityList(self)
        # else:
        #     raise TypeError("'entities' must be EntityList, list or None")

        # self.addIds()
        self.updateNeighbours()
        self.updateConnections()

    def addIds(self):
        id = 0
        for entity in self.entities:
            if(entity.power_connectable or entity.circuit_connectable):
                entity.id = str(id)
                id += 1

# Chnage how update neighbours and connections work
# Instead of finding the entity with a position, just id all entities before adding to group
# Then you can simply look at the id of the old one and overwrite the old Association
# with a new one pointing to the entity within the group's list

    def updateNeighbours(self):
        # Iterate on entities
        entity : Entity
        for entity in self.entities:
            if(entity.power_connectable):
                new_neighbours = []
                for idx in range(len(entity.neighbours)):
                    neighbour = entity.neighbours[idx]
                    na = Association(self.entities[neighbour().id])
                    entity.neighbours[idx] = na

    def updateConnections(self):
        self.find_entities_filtered
        entity : Entity
        for entity in self.entities:
            if(entity.circuit_connectable):
                for side in entity.connections:
                    if(side in {'1', '2'}):
                        for color in entity.connections[side]:
                            new_conn_data = []
                            for idx in range(len(entity.connections[side][color])):
                                point = entity.connections[side][color][idx]
                                connection = point["entity_id"]
                                na = Association(self.entities[connection().id])
                                entity.connections[side][color][idx]["entity_id"] = na