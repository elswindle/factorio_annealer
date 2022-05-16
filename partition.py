import item
import recipe
import math
from globals import *

class Partition:
    def __init__(self, item):
        self.factory_blocks = {}        # Recipe : int
        self.part_reqs = {}             # Item : rate
        self.reqs_breakdown = {}        # Item : Recipe : rate
        self.top_item = item
        self.factory_scalar = 0

    def __repr__(self):
        return self.top_item.name

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

            # Adjust rate based on actual spm
            adjusted_rate = rate * self.factory_scalar

            # is producer part of requirements
            # add to requirements or add adjusted rate to existing
            if(self.part_reqs.get(producer) is None):
                self.part_reqs[producer] = adjusted_rate
            else:
                self.part_reqs[producer] += adjusted_rate

            # does the breakdown for the producer exist
            if(self.reqs_breakdown.get(producer) is None):
                self.reqs_breakdown[producer] = {}

            # Add breakdown value going producer->recipe
            if(self.reqs_breakdown[producer].get(recipe) is None):
                self.reqs_breakdown[producer][recipe] = adjusted_rate
            else:
                self.reqs_breakdown[producer][recipe] += adjusted_rate

            # Recurse for the producer's recipe
            found = False
            # Check if producer is the top of another partition
            for part in factory.partitions.values():
                if(part.top_item == producer):
                    found = True
            if(producer.recipe != IS_RESOURCE and found == False):
                self.recurseCalculateFBR(factory, producer.recipe, rate/total_rate)

    def calculateFactoryBlockNumbers(self, factory):
        for producer in self.part_reqs.keys():
            if(producer.recipe != IS_RESOURCE):
                req_rate = self.part_reqs[producer]
                factory_block_rate = factory.block_types[producer.recipe].outputs[0].rate

                factory_block_rate = float(factory_block_rate)
                num_blocks = math.ceil(req_rate/factory_block_rate + factory.block_num_buffer)
                print(producer.name + " needs " + str(num_blocks) + " blocks")
                print("  producer: " + str(req_rate) + " " + "block: " + str(factory_block_rate))
                self.factory_blocks[producer.recipe] = num_blocks