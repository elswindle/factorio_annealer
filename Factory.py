import numpy as np
from factorycellio import FactoryCellIO
from factoryblocktemplate import FactoryBlockTemplate
from recipe import Recipe
from item import Item
import csv as csv

class Factory:
    def __init__(self, rate):
        self.science_rate = rate
        block_types = [] # FactoryBlockTemplate
        self.recipe_list = {}

    def loadFactoryRecipeList(self, path):
        recipe_csv = csv.reader(open(path), delimiter=',')
        # Skip headers
        next(recipe_csv)
        next(recipe_csv)
        next(recipe_csv)

        # formatted as follows
        # craft time
        # input1, input2...
        # output1, output2...
        # output1 is considered the output for factory requirement purposes
        # other outputs use their output value, but don't affect inputs
        for row in recipe_csv:
            craft_time = float(row[0])
            ips = next(recipe_csv)
            ops = next(recipe_csv)
            recipe_name = ops[0]

            inputs = []
            outputs = []
            for ip in ips:
                ip_item = self.item_list[ip]
                inputs.append(ip_item)

            for op in ops:
                op_item = self.item_list[op]
                outputs.append(op_item)

            new_recipe = Recipe(craft_time, inputs, outputs)
            self.recipe_list[new_recipe.name] = new_recipe

    def printFactoryRecipeList(self):
        for recipe in self.recipe_list.values():
            print(recipe)