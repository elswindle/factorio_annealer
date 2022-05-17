import deliveryvector
from globals import *

class RouteGroup:
    def __init__(self, producer, requester, tpm):
        self.producer = producer        # Item
        self.requester = requester      # Item

        self.routes = []
        self.avg_dist = -1
        self.trains_per_min = tpm       # Calculated @ partition level
        self.cost = calculateTrafficCost(self.avg_dist, self.trains_per_min)
        self.test_cost = -1

    def acceptMove(self):
        for route in self.routes:
            route.acceptMove()

        self.cost = self.test_cost

    def evaluateMove(self):
        self.test_cost = 123123123