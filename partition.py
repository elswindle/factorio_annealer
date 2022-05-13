import item
import recipe
from globals import *

class Partition:
    def __init__(self, item):
        self.num_blocks = {}
        self.part_reqs = {}
        self.reqs_breakdown = {}
        self.top_item = item
        self.factory_scalar = 0

    def calculateFactoryBlockRequirements(self, base_factory):
        import factory
        self.factory_scalar = base_factory.factory_scalar
        self.recurseCalculateFBR(base_factory, self.top_item.recipe, 1)
        
    def recurseCalculateFBR(self, factory, recipe : recipe.Recipe, share):
        for producer in recipe.inputs:
            # Get the total amount of the producer and
            # the amount of the producer going to the recipe
            # i.e. producer=gear, only 10% gear go to inserters
            # Need that to calculate the amount of iron we need for gears
            total_rate = factory.factory_reqs[producer]
            rate = factory.reqs_breakdown[producer][recipe]*share

            # is producer part of requirements
            # add to requirements or add rate to existing
            if(self.part_reqs.get(producer) is None):
                self.part_reqs[producer] = rate
            else:
                self.part_reqs[producer] += rate

            # does the breakdown for the producer exist
            if(self.reqs_breakdown.get(producer) is None):
                self.reqs_breakdown[producer] = {}

            # Add breakdown value going producer->recipe
            if(self.reqs_breakdown[producer].get(recipe) is None):
                self.reqs_breakdown[producer][recipe] = rate
            else:
                self.reqs_breakdown[producer][recipe] += rate

            # Recurse for the producer's recipe
            found = False
            # Check if producer is the top of another partition
            for part in factory.partitions:
                if(part.top_item == producer):
                    found = True
            if(producer.recipe != IS_RESOURCE and found == False):
                self.recurseCalculateFBR(factory, producer.recipe, rate/total_rate)