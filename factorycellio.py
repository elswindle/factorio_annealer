from item import Item
from factoryblocktemplates import FactoryBlockTemplate
from utils import *

if TYPE_CHECKING:
    from factorycell import FactoryCell
from routegroup import RouteGroup


class FactoryCellIO:
    def __init__(self, template, cell):
        # type: (FactoryBlockTemplate, FactoryCell) -> None
        self.item = template.item
        self.rate = template.rate
        self.direction = template.direction  # IN/OUT
        self.placement = template.placement  # TOP/BOT
        self.offset = template.location  # Offset from main cell
        self.location = -1  # -1 means unplaced
        self.tl = -1
        self.route_groups = []
        self.parent_cell = cell
        self.parent_part = cell.partition

        if self.direction == INPUT:
            self.item.is_requester.append(self)
        else:
            self.item.is_producer.append(self)

    def __repr__(self):
        if self.direction == INPUT:
            return "FCIO: " + self.item.name + " for " + self.parent_cell.recipe.name
        else:
            return "FCIO: " + self.item.name + " op"

    def addRouteGroup(self, rg):
        # type: (RouteGroup) -> None
        # found = False
        if rg not in self.route_groups:
            self.route_groups.append(rg)
        # for in_rg in self.route_groups:
        #     if in_rg == rg:
        #         found = True
        #         break

        # if not found:
        #     self.route_groups.append(rg)

    def setLocation(self, loc):
        # type: (Location) -> None
        self.location = loc
