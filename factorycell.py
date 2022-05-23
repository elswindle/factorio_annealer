import factorycellio
import factoryblocktemplates
import recipe
import item
from globals import *

class FactoryCell:
    def __init__(self, template, part_top, ips, ops, loc, is_depot=False):
        # Special case for depots
        if(is_depot == True):
            self.is_depot = True
            self.location = loc
            self.recipe = template.recipe
            return

        self.recipe = -1
        self.inputs = []
        self.outputs = []
        self.route_groups = []
        self.is_depot = False
        self.location = -1
        self.is_main = False
        self.offset = -1

        if(template != IS_RESOURCE):
            self.recipe = template.recipe
            self.part_top = part_top

            # Keep track if cell is a main or auxiliary cell
            # ATM blocks that have auxiliary cells: RC + space science
            if(loc == Location(0,0)):
                self.is_main = True
            else:
                self.is_main = False
            self.offset = loc

            for iotemp in ips:
                self.inputs.append(factorycellio.FactoryCellIO(iotemp))

            for iotemp in ops:
                self.outputs.append(factorycellio.FactoryCellIO(iotemp))

    def __repr__(self):
        return "FC: " + self.recipe.name

    def setToDepot(self):
        if(len(self.inputs) > 0 or len(self.outputs) > 0 or self.recipe == -1):
            print("attempting to set non-empty cell to Depot")
        else:
            self.is_depot = True

    def assignLocation(self, loc):
        self.location = loc