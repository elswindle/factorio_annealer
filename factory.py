import factorycellio
import factoryblocktemplates
import recipe
import item
import partition
from globals import *
from math import sqrt
from math import ceil
import csv as csv

class Factory:
    def __init__(self, rate, item_list):
        self.science_rate = rate
        self.factory_scalar = rate / 1000       # Amount to scale requirements by
        self.factory_reqs = {}                  # Item : rate
        self.reqs_breakdown = {}                # Item : Recipe : rate
        self.partitions = {}                    # Item : Partition
        self.block_types = {}                   # Recipe : FactoryBlockTemplate
        self.recipe_list = {}                   # String : Recipe
        self.item_list = item_list              # String : Item
        self.block_num_buffer = 0.1
        self.depot_ratio = 1/3
        self.dimensions = -1
        self.factory = -1

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

            new_recipe = recipe.Recipe(craft_time, inputs, outputs, True)
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
            self.block_types[recipe] = new_block

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
            if(self.reqs_breakdown.get(producer) is None):
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

    def createPartitions(self, path):
        part_csv = csv.reader(open(path, newline=''), delimiter=',')

        for top_item_str in part_csv:
            top_item = self.item_list[top_item_str]
            self.partitions[top_item] = partition.Partition(top_item)

        self.calculateFactoryBlockRequirements()
        self.calculateFactoryBlockNumbers()

    # Only call this function after all partitions have been created
    def calculateFactoryBlockRequirements(self):
        for partition in self.partitions.values():
            partition.calculateFactoryBlockRequirements(self)

    def calculateFactoryBlockNumbers(self):
        for partition in self.partitions.values():
            partition.calculateFactoryBlockNumbers(self)

    def getFactoryBlockAmount(self):
        blocks = 0
        for partition in self.partitions.values():
            blocks += partition.getFactoryBlockAmount(self)

        return blocks

    def calculateFactoryDimensions(self, aspect_ratio=1, ex_area=0):
        num_blocks = self.getFactoryBlockAmount()
        num_blocks *= 1+self.depot_ratio
        num_blocks += ex_area           # manually give it more area

        y = ceil(sqrt(num_blocks/aspect_ratio))
        x = ceil(num_blocks/y)

        self.dimensions = Dimension(x, y)
        # initialize factory, additional row+col on edges added for pins
        self.factory = [ [-1] * (x+2) for i in range(y+2)]

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