import annealer
from factorydrawer import FactoryDrawer
import game
import factory
import partition
from globals import *
import matplotlib.pyplot as plt

base_game = game.Game()

base_game.loadItemList('data/item_list.csv')
base_factory = factory.Factory(1000, base_game.item_list)

base_factory.loadFactoryRecipeList('data/recipe_list.csv')
base_factory.importBlockTemplates('data/factory_block_templates.csv')
base_factory.load1kspsRequirements('data/factory_req_1ksps.csv')

part = partition.Partition(base_game.item_list['labs'])
base_factory.partitions[base_game.item_list['labs']] = part

part2 = partition.Partition(base_game.item_list['logistic-science-pack'])
base_factory.partitions[base_game.item_list['logistic-science-pack']] = part2
part2 = partition.Partition(base_game.item_list['military-science-pack'])
base_factory.partitions[base_game.item_list['military-science-pack']] = part2
part2 = partition.Partition(base_game.item_list['automation-science-pack'])
base_factory.partitions[base_game.item_list['automation-science-pack']] = part2
part2 = partition.Partition(base_game.item_list['utility-science-pack'])
base_factory.partitions[base_game.item_list['utility-science-pack']] = part2
part2 = partition.Partition(base_game.item_list['production-science-pack'])
base_factory.partitions[base_game.item_list['production-science-pack']] = part2
part2 = partition.Partition(base_game.item_list['chemical-science-pack'])
base_factory.partitions[base_game.item_list['chemical-science-pack']] = part2
part2 = partition.Partition(base_game.item_list['space-science-pack'])
base_factory.partitions[base_game.item_list['space-science-pack']] = part2
# part2 = partition.Partition(base_game.item_list['sulfur'])
# base_factory.partitions[base_game.item_list['sulfur']] = part2


base_factory.calculateFactoryBlockRequirements()
base_factory.calculateFactoryBlockNumbers()

factory_annealer = annealer.Annealer(base_factory)
factory_annealer.initializeRouteGroups()

print("number of blocks " + str(base_factory.getFactoryBlockAmount()))

base_factory.calculateFactoryDimensions(1.2, 0)
print(base_factory.dimensions)

base_factory.populatePartitions()
base_factory.initializeBlockPlacement()
base_factory.calculatePinRequirements()
base_factory.placePins()

factory_annealer.populateRouteGroups()

fd = FactoryDrawer(base_factory)
fd.drawFactory()
plt.show()

for _ in range(2500):
    g1, g2 = factory_annealer.generateMove()
    # fd.drawFactory()
    # fd.circleGroup(g1)
    # fd.circleGroup(g2)
    # plt.show()

    factory_annealer.performMove(g1, g2)
    fd.drawFactory()
    fd.circleGroup(g1)
    fd.circleGroup(g2)
    plt.show()

fd.drawFactory()
plt.show()

print('done')