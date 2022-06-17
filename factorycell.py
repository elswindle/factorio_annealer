from factorycellio import FactoryCellIO
from factoryblocktemplates import FactoryBlockTemplate, IOTemplate
from utils import *

if TYPE_CHECKING:
    from factoryblock import FactoryBlock
    from partition import Partition

from recipe import Recipe
from item import Item


class FactoryCell:
    def __init__(self, template, part, block, ips, ops, loc, is_depot=False):
        # type: (FactoryBlockTemplate, Partition, FactoryBlock, list[IOTemplate], list[IOTemplate], Location, bool) -> None
        # Special case for depots
        if is_depot == True:
            self.is_depot = True
            self.location = loc
            self.recipe = template.recipe
            self.parent_block = -1
            self.offset = Location(0, 0)
            self.tl = -1
            return

        self.recipe = -1
        self.inputs = []
        self.outputs = []
        self.route_groups = []
        self.is_depot = False
        self.location = -1
        self.tl = -1
        self.is_main = False
        self.offset = -1

        if template != IS_RESOURCE:
            self.recipe = template.recipe
            self.partition = part
            self.parent_block = block

            # Keep track if cell is a main or auxiliary cell
            # ATM blocks that have auxiliary cells: RC + space science
            if loc == Location(0, 0):
                self.is_main = True
            else:
                self.is_main = False
            self.offset = loc

            for iotemp in ips:
                self.inputs.append(FactoryCellIO(iotemp, self))

            for iotemp in ops:
                self.outputs.append(FactoryCellIO(iotemp, self))
        else:  # for resource
            print("resource")

    def __repr__(self):
        return "FC: " + self.recipe.name

    def setLocation(self, block_loc):
        # type: (Location) -> None
        self.location = block_loc + self.offset
        if self.location.x > 35 and self.recipe == EMPTY:
            print("help the cell")
        if not self.is_depot:
            for ip in self.inputs:
                ip.location = self.location
            for op in self.outputs:
                op.location = self.location

    def setTestLocation(self, block_loc):
        # type: (Location) -> None
        self.tl = block_loc + self.offset
        if not self.is_depot:
            for ip in self.inputs:
                ip.tl = self.tl
            for op in self.outputs:
                op.tl = self.tl

    def resetTestLocation(self):
        self.tl = -1
        if not self.is_depot:
            for ip in self.inputs:
                ip.tl = self.tl
            for op in self.outputs:
                op.tl = self.tl

    def setToDepot(self):
        if len(self.inputs) > 0 or len(self.outputs) > 0 or self.recipe == -1:
            print("attempting to set non-empty cell to Depot")
        else:
            self.is_depot = True

    def assignLocation(self, loc):
        # type: (Location) -> None
        self.location = loc
