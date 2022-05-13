import game
import factory
from globals import *

base_game = game.Game()

base_game.loadItemList('data/item_list.csv')
factory = factory.Factory(1000, base_game.item_list)

factory.loadFactoryRecipeList('data/recipe_list.csv')
factory.importBlockTemplates('data/factory_block_templates.csv')
factory.printBlockTemplates()