import factorycellio
import factoryblocktemplates
import recipe
import item
from globals import *

class FactoryCell:
    def __init__(self, template, part_top):
        self.recipe = -1
        self.inputs = []
        self.outputs = []
        self.pcells = []
        self.route_groups = []
        self.is_depot = False

        if(template != IS_RESOURCE):
            self.recipe = template.recipe
            self.part_top = part_top

            for iotemp in template.inputs:
                self.inputs.append(factorycellio.FactoryCellIO(iotemp))

            for iotemp in template.outputs:
                self.outputs.append(factorycellio.FactoryCellIO(iotemp))

            for loc in template.pcells:
                self.pcells.append(loc)

    def setToDepot(self):
        if(len(self.inputs) > 0 or len(self.outputs) > 0 or self.recipe == -1):
            print("attempting to set non-empty cell to Depot")
        else:
            self.is_depot = True