import numpy as np
import factorycellio
import factoryblocktemplates
import recipe
import item
from globals import *
import csv as csv

class Factory:
    def __init__(self, rate, item_list):
        self.science_rate = rate
        self.factory_reqs = {}
        self.block_types = {} # FactoryBlockTemplate
        self.recipe_list = {}
        self.item_list = item_list

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

            new_recipe = recipe.Recipe(craft_time, inputs, outputs)
            self.recipe_list[new_recipe.name] = new_recipe

    def importBlockTemplates(self, path):
        block_csv = csv.reader(open(path, newline=''), delimiter=',')
        # Skip headers
        next(block_csv)
        next(block_csv)
        next(block_csv)
        # initialize row, should be equal to the final row of the header
        row = next(block_csv)
        # Iterate until the end of file (explicitly defined in txt file)
        while(row[0] != 'EOF'):
            # Retrieve recipe from list
            recipe = self.recipe_list[row[0]]
            new_block = factoryblocktemplates.FactoryBlockTemplate(recipe, block_csv, self.item_list)
            self.block_types[recipe.name] = new_block

            # Get next name, if EOF, end loop
            row = next(block_csv)

    def printFactoryRecipeList(self):
        for recipe in self.recipe_list.values():
            print(recipe)

    def printBlockTemplates(self):
        for block in self.block_types.values():
            print(block)