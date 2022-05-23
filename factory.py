import factorycellio
import factoryblocktemplates
import factorycell
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
        self.block_templates = {}                   # Recipe : FactoryBlockTemplate
        self.recipe_list = {}                   # String : Recipe
        self.item_list = item_list              # String : Item
        self.block_num_buffer = 0.1
        self.depot_ratio = 1/4
        self.dimensions = -1
        self.factory = -1                       # FactoryCells[x][y]
        self.placement_ptr = Location(1,1)      # keeps track of location to place next block

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
            self.block_templates[recipe] = new_block

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
        num_blocks += ex_area           # manually give it more area
        num_blocks *= 2                 # Depots will be initially place every other row

        y = ceil(sqrt(num_blocks/aspect_ratio))+1
        x = ceil(num_blocks/y)+1
        
        # This is here to make sure there are an odd number of rows
        # so that top and bottom rows will be factory blocks, not
        # depots
        if(y % 2 == 0):
            y += 1

        self.dimensions = Dimension(x, y)
        # initialize factory, additional row+col on edges added for pins
        self.factory = [ [-1] * (y+2) for i in range(x+2)]

    def populatePartitions(self):
        for part in self.partitions.values():
            part.populateFactoryBlocks(self)

    def initializeBlockPlacement(self):
        depot = factoryblocktemplates.FactoryBlockTemplate(recipe.Recipe('depot', -1, -1, -1), -1, -1)
        for part in self.partitions.values():
            for block in part.factory_blocks:
                # Make sure block can fit in available location
                # Check for different sized blocks
                anchor = Location(block.num_left, block.num_below)
                if(block.dimension != Dimension(1,1)):                    
                    # Check if block will fit in current location
                    space_left = self.dimensions.x - block.dimension.x - self.placement_ptr.x + 1
                    if(space_left <= 0):
                        # place depots instead
                        while(self.placement_ptr.x <= self.dimensions.x):
                            x = self.placement_ptr.x
                            y = self.placement_ptr.y
                            self.factory[x][y] = factorycell.FactoryCell(depot, -1, -1, -1, self.placement_ptr, True)

                            self.placement_ptr.x += 1

                        # Set pointer to next row
                        self.placement_ptr.y += 1
                        self.placement_ptr.x = 1

                        if(self.placement_ptr.y % 2 == 0):
                            # Place row of depots
                            for i in range(self.dimensions.x):
                                x = self.placement_ptr.x
                                y = self.placement_ptr.y

                                self.factory[x][y] = factorycell.FactoryCell(depot, -1, -1, -1, Location(x,y), True)
                                self.placement_ptr.x += 1

                            self.placement_ptr.y += 1
                            self.placement_ptr.x = 1

                block.location = anchor + self.placement_ptr
                for fcell in block.fcells:
                    fcell.location = block.location + fcell.offset
                    self.factory[fcell.location.x][fcell.location.y] = fcell

                # Update pointer
                self.placement_ptr.x += block.dimension.x
                # Check if pointer has reached end of row
                if(self.placement_ptr.x > self.dimensions.x):
                    self.placement_ptr.y += 1
                    self.placement_ptr.x = 1

                    # Initially place depots every other row
                    # Depots will get pushed out by annealing
                    if(self.placement_ptr.y % 2 == 0):
                        # Place row of depots
                        for i in range(self.dimensions.x):
                            x = self.placement_ptr.x
                            y = self.placement_ptr.y

                            self.factory[x][y] = factorycell.FactoryCell(depot, -1, -1, -1, Location(x,y), True)
                            self.placement_ptr.x += 1

                        self.placement_ptr.y += 1
                        self.placement_ptr.x = 1

                # Skip already filled spaces
                while(self.factory[self.placement_ptr.x][self.placement_ptr.y] != EMPTY):
                    self.placement_ptr.x += 1

                    # Check if pointer has reached end of row
                    if(self.placement_ptr.x > self.dimensions.x):
                        self.placement_ptr.y += 1
                        self.placement_ptr.x = 1

                        # Initially place depots every other row
                        # Depots will get pushed out by annealing
                        if(self.placement_ptr.y % 2 == 0):
                            # Place row of depots
                            for i in range(self.dimensions.x):
                                x = self.placement_ptr.x
                                y = self.placement_ptr.y

                                self.factory[x][y] = factorycell.FactoryCell(depot, -1, -1, -1, self.placement_ptr, True)
                                self.placement_ptr.x += 1

                            self.placement_ptr.y += 1
                            self.placement_ptr.x = 1

    def printFactoryRecipeList(self):
        for recipe in self.recipe_list.values():
            print(recipe)

    def printBlockTemplates(self):
        for block in self.block_templates.values():
            print(block)

    def print1kspsRequirements(self):
        for item in self.factory_reqs.keys():
            print(item.name + " must produce " + str(self.factory_reqs[item]) + "/min")
            print(item.name + " is requested by the following recipes")

            for requester in self.reqs_breakdown[item].keys():
                print("\t" + requester.name + " requests " + str(self.reqs_breakdown[item][requester]) + "/min")