from utils import *
from item import Item
from recipe import Recipe

if TYPE_CHECKING:
    from factorycellio import FactoryCellIO


class RouteGroup:
    def __init__(self, producer, requester, tpm):
        # type: (Item, Recipe, float) -> None
        self.producer = producer  # Item
        self.requester = requester  # Recipe

        self.routes = {}  # type: Mapping[FactoryCellIO, FactoryCellIO]
        self.producers = []  # type: list[FactoryCellIO]
        self.requesters = []  # type: list[FactoryCellIO]
        self.avg_dist = -1
        self.trains_per_min = tpm  # Calculated @ partition level
        self.cost = calculateTrafficCost(self.avg_dist, self.trains_per_min)
        self.test_cost = -1

    def __repr__(self):
        return self.producer.name + " to " + self.requester.name

    def acceptMove(self):
        for route in self.routes:
            route.acceptMove()

        self.cost = self.test_cost

    def evaluateMove(self):
        self.test_cost = 123123123
