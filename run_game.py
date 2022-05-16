import game
import factory
import partition
from globals import *

base_game = game.Game()

base_game.loadItemList('data/item_list.csv')
base_factory = factory.Factory(1000, base_game.item_list)

base_factory.loadFactoryRecipeList('data/recipe_list.csv')
base_factory.importBlockTemplates('data/factory_block_templates.csv')
base_factory.load1kspsRequirements('data/factory_req_1ksps.csv')

part = partition.Partition(base_game.item_list['research'])
part.calculateFactoryBlockRequirements(base_factory)
part.calculateFactoryBlockNumbers(base_factory)

print('done')