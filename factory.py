import numpy as np
from sklearn.metrics import top_k_accuracy_score
import factorycellio
import factoryblocktemplates
import recipe
import item
import partition
from globals import *
import csv as csv

class Factory:
    def __init__(self, rate, item_list):
        self.science_rate = rate
        self.factory_scalar = rate / 1000       # Amount to scale requirements by
        self.factory_reqs = {}                  # Item : rate
        self.reqs_breakdown = {}                # Item : Recipe : rate
        self.partitions = {}                    # Item : Partition
        self.block_types = {}                   # Recipe : FactoryBlockTemplate
        self.recipe_list = {}                   # Item : Recipe
        self.item_list = item_list              # String : Item

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

    def load1kspsRequirements(self, path):
        # Expected format:
        # producer,rate
        # req,requester,x,y,placement(,rate (if o/p))
        # ...
        # end
        csv_req = csv.reader(open(path, newline=''), delimiter=',')
        # throw out header
        next(csv_req)
        next(csv_req)
        next(csv_req)

        for row in csv_req:
            # Get producer
            producer = self.item_list[row[0]]
            self.factory_reqs[producer] = float(row[1])
            # Check if breakdown has dictionary for producer
            if(~(producer in self.reqs_breakdown)):
                self.reqs_breakdown[producer] = {}

            # Iterate on requesters
            row = next(csv_req)
            while(row[0] != 'end'):
                # Check if line is requester (no other options atm)
                if(row[0] == 'req'):
                    requester = self.recipe_list[row[1]]
                    # Set producer->requester item rate
                    self.reqs_breakdown[producer][requester] = float(row[2])

                row = next(csv_req)

        # Sanity check
        for item in self.factory_reqs.keys():
            total = self.factory_reqs[item]
            sum = 0
            for requester in self.reqs_breakdown[item].values():
                sum += requester

            # Check if summations are within in 2% of total
            if(total < sum*1.02 and total > sum*0.98):
                print("requirement breakdown acceptable for " + item.name)
            else:
                print("revisit " + item.name + " and find error")
                print("total: " + str(self.factory_reqs[item]))
                print("sum = " + str(sum))

    def createPartitions(self, path):
        part_csv = csv.reader(open(path, newline=''), delimiter=',')

        for top_item_str in part_csv:
            top_item = self.item_list[top_item_str]
            self.partitions[top_item] = partition.Partition(top_item)

    def calculateFactoryBlockRequirements(self):
        # This will move to partitions
        # for partition in self.partitions:
        #   partition.calculateFactoryBlockRequirements(self)
        self.x = 69

    def printFactoryRecipeList(self):
        for recipe in self.recipe_list.values():
            print(recipe)

    def printBlockTemplates(self):
        for block in self.block_types.values():
            print(block)

    def print1kspsRequirements(self):
        for item in self.factory_reqs.keys():
            print(item.name + " must produce " + str(self.factory_reqs[item]) + "/min")
            print(item.name + " is requested by the following recipes")

            for requester in self.reqs_breakdown[item].keys():
                print("\t" + requester.name + " requests " + str(self.reqs_breakdown[item][requester]) + "/min")