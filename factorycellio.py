import item
import factoryblocktemplates
from globals import *

class FactoryCellIO:
    def __init__(self, template):
        self.item = template.item
        self.rate = template.rate
        self.direction = template.direction
        self.placement = template.placement
        self.location = template.location
        self.route_groups = []

    def addRouteGroup(self, rg):
        self.route_groups.append(rg)
