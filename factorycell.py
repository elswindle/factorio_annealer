import factorycellio
import factoryblocktemplates
import recipe
import item
from globals import *

class FactoryCell:
    def __init__(self, template, part_top):
        self.recipe = template.recipe
        self.inputs = []
        self.outputs = []
        self.pcells = []
        self.route_groups = []
        self.is_depot = False

        if(template != -1):
            self.part_top = part_top

            for iotemp in template.inputs:
                self.inputs.append(factorycellio.FactoryCellIO(iotemp))

            for iotemp in template.outputs:
                self.outputs.append(factorycellio.FactoryCellIO(iotemp))

            for loc in template.pcells:
                self.pcells.append(loc)
        else:
            self.pcells.append(Location(0,0))
            self.is_depot = True