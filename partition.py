from item import Item
from recipe import Recipe
from utils import *
from factoryblock import FactoryBlock
import factorycalculator as calculator

if TYPE_CHECKING:
    from factory import Factory
    from routegroup import RouteGroup

import math


class Partition:
    def __init__(self, item, id, main=False, rate=0):
        # type: (Item, int, bool, float) -> None
        self.num_factory_blocks = {}  # type: Mapping[Recipe, int]
        self.part_reqs = {}  # type: Mapping[Item, float]
        self.reqs_breakdown = {}  # type: Mapping[Item, Mapping[Recipe, float]]
        self.top_item = item
        self.factory_blocks = []  # type: list[FactoryBlock]
        # This will be calculated later after population
        self.partition_scalar = rate
        self.main = main
        self.id = id

    def __repr__(self):
        return self.top_item.name + " is top"

    def calculateNormalizedPartitionRequirements(self, factory):
        calculator.calculateNormalizedRequirements(
            factory, self.part_reqs, self.reqs_breakdown, self.top_item
        )

    def calculateFactoryBlockRequirements(self, base_factory):
        # type: (Factory) -> None
        self.factory_scalar = base_factory.factory_scalar
        top_recipes = []
        for recipe in base_factory.recipe_list.values():
            for input in recipe.inputs:
                if self.top_item == input:
                    top_recipes.append(recipe)
                    # break

        # Start recursion on recipe that requests top item
        # This will result in the top item of a partition to be counted
        # twice, once in the partition and the partition that contains
        # the requesting recipe
        # For example, logisitic-science-pack factory block requirements
        # (for the item itself, not dependencies) will be both in its
        # own partition but in the research partition as well
        for top_recipe in top_recipes:
            self.recurseCalculateFBR(base_factory, top_recipe, 1, True)

    def recurseCalculateFBR(self, factory, recipe, share, is_top=False):
        # type: (Factory, Recipe, float, bool) -> None
        for producer in recipe.ingredients:
            # Special treatment for top item's requester
            # Don't process anything from top's requester if it isn't top
            if is_top:
                if producer != self.top_item:
                    continue

            # print(recipe.name)
            # print(producer.name)
            # Get the total amount of the producer and
            # the amount of the producer going to the recipe
            # i.e. producer=gear, only 10% gear go to inserters
            # Need that to calculate the amount of iron we need for gears
            total_rate = factory.factory_reqs[producer]
            rate = factory.reqs_breakdown[producer][recipe] * share

            # Adjust rate based on actual spm
            adjusted_rate = rate * self.factory_scalar
            # print("tr: " + str(total_rate) + " r: " + str(rate) + " ar: " + str(adjusted_rate))
            # is producer part of requirements
            # add to requirements or add adjusted rate to existing
            if self.part_reqs.get(producer) is None:
                self.part_reqs[producer] = adjusted_rate
            else:
                self.part_reqs[producer] += adjusted_rate

            # does the breakdown for the producer exist
            if self.reqs_breakdown.get(producer) is None:
                self.reqs_breakdown[producer] = {}

            # Add breakdown value going producer->recipe
            if self.reqs_breakdown[producer].get(recipe) is None:
                self.reqs_breakdown[producer][recipe] = adjusted_rate
            else:
                self.reqs_breakdown[producer][recipe] += adjusted_rate

            # Recurse for the producer's recipe
            found = False
            # Check if producer is the top of another partition, not current
            for part in factory.partitions.values():
                if part.top_item == producer:
                    if part != self:
                        # if(not self.top_item == part.top_item):
                        found = True
            if not producer.is_resource and found == False:
                self.recurseCalculateFBR(factory, producer.recipe, rate / total_rate)

    def calculateFactoryBlockNumbers(self, factory):
        # type: (Factory) -> None
        for producer in self.part_reqs.keys():
            if not producer.is_resource:
                req_rate = self.part_reqs[producer] * self.partition_scalar
                factory_block_rate = (
                    factory.block_templates[producer.preferred_recipe].outputs[0].rate
                )

                factory_block_rate = float(factory_block_rate)
                num_blocks = math.ceil(
                    req_rate / factory_block_rate + factory.block_num_buffer
                )
                print(producer.name + " needs " + str(num_blocks) + " blocks")
                print(
                    "  producer: "
                    + str(req_rate)
                    + " "
                    + "block: "
                    + str(factory_block_rate)
                )
                self.num_factory_blocks[producer.preferred_recipe] = num_blocks

    def getFactoryBlockAmount(self, base_factory):
        # type: (Factory) -> int
        blocks = 0
        for block in self.num_factory_blocks.keys():
            # Search for other partitions top item and don't include it
            found = False
            for part in base_factory.partitions.values():
                # Only include top item blocks of current partition
                if part != self and part.top_item == block.item:
                    # Check if block item and partition top item are equal
                    found = True

            if not found:
                blocks += self.num_factory_blocks[block]

        return blocks

    def getFactoryCellAmount(self):
        # type: () -> int
        cells = 0
        for block in self.factory_blocks:
            cells += len(block.fcells)

        return cells

    def populateFactoryBlocks(self, factory):
        # type: (Factory) -> None
        for recipe in self.num_factory_blocks.keys():
            template = factory.block_templates[recipe]
            # Check if recipe is a top level item of partition
            found = False
            for part in factory.partitions.values():
                if part != self and part.top_item == recipe.item:
                    found = True

            if not found:
                for i in range(self.num_factory_blocks[recipe]):
                    new_block = FactoryBlock(template, self)
                    self.factory_blocks.append(new_block)
            else:
                print(recipe.name + " is top item of a partition, skipping")

    def populateRouteGroups(self, factory, rgs):
        # type: (Factory, Mapping[Item, Mapping[Recipe, RouteGroup]]) -> None
        # rg is sub dictionary of annealer's rg
        # rg[item (pro)][recipe (req)] = RouteGroup
        for item in rgs.keys():
            item_is_top = False
            for part in factory.partitions.values():
                if part.top_item == item:
                    item_is_top = True
                    break

            # Iterate on FactoryCellIOs that request the item
            requester_recipe = None
            for requester in item.is_requester:
                # Make sure IO is in current partition
                if requester.parent_part == self:
                    # Get the recipe that requests the item
                    requester_recipe = requester.parent_cell.recipe

                    # Add requester IO to route group and add route group to IO
                    rgs[item][requester_recipe].requesters.append(requester)
                    requester.addRouteGroup(rgs[item][requester_recipe])

            # Iterate on FactoryCellIOs that produce the item
            for producer in item.is_producer:
                # Only look at producers within the current partition
                # Also always accept resources if not partitioning pins
                # !partitionPins & is_resouce
                resource_accept = not factory.partitionPins and item.is_resource
                if producer.parent_part == self or item_is_top or resource_accept:
                    for rg in rgs[item].values():
                        rg.producers.append(producer)
                        producer.addRouteGroup(rg)

            # for rg in rgs[item].values():
            #     for producer in item.is_producer:
            #         found = False
            #         for part in factory.partitions.values():
            #             if part.top_item == item:
            #                 found = True
            #         if producer.parent_part == self or found or item.is_resource:
            #             rg.producers.append(producer)
            #             producer.addRouteGroup(rg)

            # This isn't used...
            # Iterate on FactoryCellIOs that produce item
            # for producer in item.is_producer:
            #     found = False
            #     for part in factory.partitions.values():
            #         if part.top_item == item:
            #             found = True
            #     # Only look at producers in the current partition or if a top level partition item
            #     # Resources are shared among all partitions
            #     if producer.parent_part == self or found:
            #         # Iterate on FactoryCellIOs that request item
            #         for requester in item.is_requester:
            #             # Only look at requesters in the current partition or is resource
            #             if requester.parent_part == self:
            #                 # Get the recipe of the requester
            #                 requester_recipe = requester.parent_cell.recipe

            #                 rg = rgs[item][requester_recipe]

            #                 # Add list for FactoryCellIO producer
            #                 if rg.routes.get(producer) is None:
            #                     rg.routes[producer] = []

            #                 # Add destination FactoryCellIO
            #                 rg.routes[producer].append(requester)
