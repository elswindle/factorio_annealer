import item
import factoryblocktemplates
from globals import *

class FactoryCellIO:
    def __init__(self, template):
        self.item = template.item
        self.rate = template.rate
        self.direction = template.direction # IN/OUT
        self.placement = template.placement # TOP/BOT
        self.offset = template.location     # Offset from main cell
        self.location = -1                  # -1 means unplaced
        self.route_groups = []

    def __repr__(self):
        return "FCIO: " + self.item.name

    def addRouteGroup(self, rg):
        self.route_groups.append(rg)

    def setLocation(self, loc):
        self.location = loc
