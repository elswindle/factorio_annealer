from annealer import Annealer
from factorydrawer import FactoryDrawer
from game import Game
from factory import Factory
from partition import Partition
from utils import *
import matplotlib.pyplot as plt
from blueprinter import Blueprinter

# bptr = blueprinter.Blueprinter()
# bptr.testEntityTransfer()
# bptr = Blueprinter("data/micro_blocks_v0.9.txt")
# bptr.test123('data/labs_with_circuits.txt')
# bptr.testFactoryBlueprint()

base_game = Game()

base_game.loadItemList("data/item_list.csv")
base_factory = Factory(2000, base_game.item_list)

base_factory.loadFactoryRecipeList("data/recipe_list.csv")
base_factory.importBlockTemplates("data/factory_block_templates.csv")
base_factory.load1kspsRequirements("data/factory_req_1ksps.csv")

# part = Partition(base_game.item_list['labs'])
# base_factory.partitions[base_game.item_list['labs']] = part

# part2 = Partition(base_game.item_list["logistic-science-pack"])
# base_factory.partitions[base_game.item_list["logistic-science-pack"]] = part2
# part2 = Partition(base_game.item_list['military-science-pack'])
# base_factory.partitions[base_game.item_list['military-science-pack']] = part2
# part2 = Partition(base_game.item_list['automation-science-pack'])
# base_factory.partitions[base_game.item_list['automation-science-pack']] = part2
# part2 = Partition(base_game.item_list['utility-science-pack'])
# base_factory.partitions[base_game.item_list['utility-science-pack']] = part2
# part2 = Partition(base_game.item_list['production-science-pack'])
# base_factory.partitions[base_game.item_list['production-science-pack']] = part2
part2 = Partition(base_game.item_list["chemical-science-pack"])
base_factory.partitions[base_game.item_list["chemical-science-pack"]] = part2
# part2 = Partition(base_game.item_list['space-science-pack'])
# base_factory.partitions[base_game.item_list['space-science-pack']] = part2
# part2 = Partition(base_game.item_list['sulfur'])
# base_factory.partitions[base_game.item_list['sulfur']] = part2


base_factory.calculateFactoryBlockRequirements()
base_factory.calculateFactoryBlockNumbers()

factory_annealer = Annealer(base_factory)
factory_annealer.initializeRouteGroups()

print("number of blocks " + str(base_factory.getFactoryBlockAmount()))

base_factory.populatePartitions()
base_factory.calculateFactoryDimensions(1.6, 0)
print(base_factory.dimensions)
base_factory.initializeBlockPlacement()
base_factory.calculatePinRequirements()
base_factory.placePins()
base_factory.populateTestFactory()
factory_annealer.populateRouteGroups()

fd = FactoryDrawer(base_factory)
# fd.drawFactory()
# plt.show()

for _ in range(25000):
    if _ % 1000 == 0:
        print(_)
        base_factory.validateFactoryCellLocations()
        # fd.drawFactory()
        # plt.show()
    g1, g2 = factory_annealer.generateMove()
    # fd.drawFactory()
    # fd.circleGroup(g1,'b')
    # fd.circleGroup(g2)
    # factory_annealer.evaluateMove(g1, g2)
    # plt.show()

    if factory_annealer.evaluateMove(g1, g2):
        factory_annealer.performMove(g1, g2)

# g1, g2 = factory_annealer.generateMove()
# factory_annealer.setTestLocations(g1, g2)
# fd.drawFactory()
# fd.circleGroup(g1,'b')
# fd.circleGroup(g2)
# factory_annealer.evaluateMove(g1, g2, fd)
# plt.show()

# g1, g2 = factory_annealer.generateMove()
# factory_annealer.setTestLocations(g1, g2)
fd.drawFactory()
# fd.circleGroup(g1,'b')
# fd.circleGroup(g2)
# factory_annealer.evaluateMove(g1, g2, fd)
plt.show()

print("done")
