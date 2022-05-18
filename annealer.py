import factory
from globals import *
import routegroup

class Annealer:
    def __init__(self, factory : factory.Factory):
        self.factory = factory
        self.route_groups = {}              # Partition : Item : Recipe : RouteGroup
        self.temperature = INITIAL_TEMP

    def initializeRouteGroups(self):
        for part in self.factory.partitions.values():
            reqs_bd = part.reqs_breakdown
            if(self.route_groups.get(part) is None):
                self.route_groups[part] = {}

            # Iterate item requirements
            for producer in reqs_bd.keys():                 # producer is Item
                if(self.route_groups[part].get(producer) is None):
                    self.route_groups[part][producer] = {}
                # Iterate on recipe requesters
                for requester in reqs_bd[producer].keys():  # requester is Recipe
                    rate = reqs_bd[producer][requester]
                    stack_size = producer.stack_size
                    if(producer.is_fluid):
                        train_size = 25000
                    else:
                        train_size = stack_size * 40
                    tpm = rate / train_size                 # Trains have 40 inventory slots
                    new_rg = routegroup.RouteGroup(producer, requester, tpm)
                    
                    self.route_groups[part][producer][requester] = new_rg

    def populateRouteGroups(self):
        # Iterate through partitions
        for part in self.route_groups.keys():
            print("hi")
            