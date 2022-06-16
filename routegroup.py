import deliveryvector
from globals import *


class RouteGroup:
    def __init__(self, producer, requester, tpm):
        self.producer = producer  # Item
        self.requester = requester  # Recipe

        self.routes = {}  # FactoryCellIO : FactoryCellIO
        self.producers = []  # FactoryCellIO
        self.requesters = []  # FactoryCellIO
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
