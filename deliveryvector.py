from globals import *

class DeliveryVector:
    def __init__(self, producer, requester):
        self.producer = producer
        self.requester = requester
        self.test_dist = -1
        self.distance = calculateDistanceCost(producer.location, requester.location, requester.placement)