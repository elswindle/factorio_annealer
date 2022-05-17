from globals import *

class DeliveryVector:
    def __init__(self, producer, requester):
        self.producer = producer
        self.requester = requester
        self.test_dist = -1
        self.distance = calculateDistanceCost(self.producer.location, self.requester.location, self.requester.placement)

    def acceptMove(self):
        self.distance = self.test_dist
        self.test_dist = -1

    def calculateTestDistance(self):
        self.test_dist = calculateDistanceCost(self.producer.location, self.requester.location, self.requester.placement)