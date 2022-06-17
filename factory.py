from factorycellio import FactoryCellIO
from factoryblocktemplates import FactoryBlockTemplate
from factorycell import FactoryCell
from factoryblock import FactoryBlock
from recipe import Recipe
from item import Item
from partition import Partition
from utils import *
from math import ceil, floor, sqrt
import csv as csv


class Factory:
    def __init__(self, rate, item_list):
        # type: (float, list[Item]) -> None
        self.science_rate = rate
        self.factory_scalar = rate / 1000  # Amount to scale requirements by
        self.factory_reqs = {}  # Item : rate
        self.pin_reqs = {}  # Item (Resource) : num pins
        self.pin_blocks = []  # FactoryBlock
        self.reqs_breakdown = {}  # Item : Recipe : rate
        self.partitions = {}  # Item : Partition
        self.block_templates = {}  # Recipe : FactoryBlockTemplate
        self.recipe_list = {}  # String : Recipe
        self.item_list = item_list  # String : Item
        self.block_num_buffer = 0.1
        self.depot_ratio = 1 / 4
        self.dimensions = -1
        self.factory = -1  # FactoryCells[x][y]
        self.tf = -1  # same as factory, but the test one
        self.placement_ptr = Location(
            1, 1
        )  # keeps track of location to place next block

    def loadFactoryRecipeList(self, path):
        # type: (str) -> None
        recipe_csv = csv.reader(open(path), delimiter=",")
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

            new_recipe = Recipe(craft_time, inputs, outputs, True)
            self.recipe_list[new_recipe.name] = new_recipe

    def importBlockTemplates(self, path):
        # type: (str) -> None
        block_csv = csv.reader(open(path, newline=""), delimiter=",")
        # Skip headers
        next(block_csv)
        next(block_csv)
        next(block_csv)
        # initialize row, should be equal to the final row of the header
        row = next(block_csv)
        # Iterate until the end of file (explicitly defined in txt file)
        while row[0] != "EOF":
            # Retrieve recipe from list
            recipe = self.recipe_list[row[0]]
            new_block = FactoryBlockTemplate(recipe, block_csv, self.item_list)
            self.block_templates[recipe] = new_block

            # Get next name, if EOF, end loop
            row = next(block_csv)

    def load1kspsRequirements(self, path):
        # type: (str) -> None
        # Expected format:
        # producer,rate
        # req,requester,x,y,placement(,rate (if o/p))
        # ...
        # end
        csv_req = csv.reader(open(path, newline=""), delimiter=",")
        # throw out header
        next(csv_req)
        next(csv_req)
        next(csv_req)

        for row in csv_req:
            # Get producer
            producer = self.item_list[row[0]]
            self.factory_reqs[producer] = float(row[1])
            # Check if breakdown has dictionary for producer
            if self.reqs_breakdown.get(producer) is None:
                self.reqs_breakdown[producer] = {}

            # Iterate on requesters
            row = next(csv_req)
            while row[0] != "end":
                # Check if line is requester (no other options atm)
                if row[0] == "req":
                    requester = self.recipe_list[row[1]]
                    # Set producer->requester item rate
                    self.reqs_breakdown[producer][requester] = float(row[2])

                row = next(csv_req)

    def createPartitions(self, path):
        # type: (str) -> None
        part_csv = csv.reader(open(path, newline=""), delimiter=",")

        for top_item_str in part_csv:
            top_item = self.item_list[top_item_str]
            self.partitions[top_item] = Partition(top_item)

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

        self.num_blocks = blocks
        return blocks

    def getFactoryCellAmount(self):
        cells = 0
        for partition in self.partitions.values():
            cells += partition.getFactoryCellAmount()

        return cells

    def calculateFactoryDimensions(self, aspect_ratio=1, ex_area=0):
        # type: (float, int) -> None
        num_cells = self.getFactoryCellAmount()
        num_cells += ex_area  # manually give it more area
        num_cells *= 2  # Depots will be initially place every other row

        x = ceil(sqrt(num_cells * aspect_ratio))
        y = ceil(num_cells / x)

        # This is here to make sure there are an odd number of rows
        # so that top and bottom rows will be factory blocks, not
        # depots
        if y % 2 == 0:
            y -= 1
            num_cells -= x

        self.spare_slots = x * y - num_cells
        self.dimensions = Dimension(x, y)
        # initialize factory, additional row+col on edges added for pins
        self.factory = [[EMPTY] * (y + 2) for i in range(x + 2)]
        self.tf = [[EMPTY] * (y + 2) for i in range(x + 2)]

    def populatePartitions(self):
        for part in self.partitions.values():
            part.populateFactoryBlocks(self)

    def initializeBlockPlacement(self):
        depot = FactoryBlockTemplate(Recipe("depot", -1, -1, -1), -1, -1)
        placed_blocks = 0
        for part in self.partitions.values():
            for block in part.factory_blocks:
                # Make sure block can fit in available location
                # Check for different sized blocks
                anchor = Location(block.num_left, block.num_below)
                if block.dimension != Dimension(1, 1):
                    # Check if block will fit in current location
                    space_left = (
                        self.dimensions.x - block.dimension.x - self.placement_ptr.x + 1
                    )
                    if space_left <= 0:
                        # place depots instead
                        while self.placement_ptr.x <= self.dimensions.x:
                            x = self.placement_ptr.x
                            y = self.placement_ptr.y
                            self.factory[x][y] = FactoryCell(
                                depot, -1, -1, -1, -1, Location(x, y), True
                            )

                            self.placement_ptr.x += 1
                            # Placing a depot in a designated cell location
                            # reduces the number of available locations given the current dimensions
                            self.spare_slots -= 1

                        # If spare slots ever is negative, add 2 more rows
                        if self.spare_slots < 0:
                            self.dimensions.y += 2
                            self.spare_slots += x
                            for col in self.tf:
                                col.append(EMPTY)
                                col.append(EMPTY)
                            for col in self.factory:
                                col.append(EMPTY)
                                col.append(EMPTY)

                        # Set pointer to next row
                        self.placement_ptr.y += 1
                        self.placement_ptr.x = 1

                        if self.placement_ptr.y % 2 == 0:
                            # Place row of depots
                            for i in range(self.dimensions.x):
                                x = self.placement_ptr.x
                                y = self.placement_ptr.y

                                self.factory[x][y] = FactoryCell(
                                    depot, -1, -1, -1, -1, Location(x, y), True
                                )
                                self.placement_ptr.x += 1

                            self.placement_ptr.y += 1
                            self.placement_ptr.x = 1

                block.location = anchor + self.placement_ptr
                for fcell in block.fcells:
                    fcell.setLocation(block.location)
                    # fcell.location = block.location + fcell.offset
                    self.factory[fcell.location.x][fcell.location.y] = fcell

                placed_blocks += 1

                # Update pointer
                self.placement_ptr.x += block.dimension.x
                # Check if pointer has reached end of row
                if (
                    self.placement_ptr.x > self.dimensions.x
                    and placed_blocks < self.num_blocks
                ):
                    self.placement_ptr.y += 1
                    self.placement_ptr.x = 1

                    # Initially place depots every other row
                    # Depots will get pushed out by annealing
                    if self.placement_ptr.y % 2 == 0:
                        # Place row of depots
                        for i in range(self.dimensions.x):
                            x = self.placement_ptr.x
                            y = self.placement_ptr.y

                            self.factory[x][y] = FactoryCell(
                                depot, -1, -1, -1, -1, Location(x, y), True
                            )
                            self.placement_ptr.x += 1

                        self.placement_ptr.y += 1
                        self.placement_ptr.x = 1

                # Skip already filled spaces
                while self.factory[self.placement_ptr.x][self.placement_ptr.y] != EMPTY:
                    self.placement_ptr.x += 1

                    # Check if pointer has reached end of row
                    if self.placement_ptr.x > self.dimensions.x:
                        self.placement_ptr.y += 1
                        self.placement_ptr.x = 1

                        # Initially place depots every other row
                        # Depots will get pushed out by annealing
                        if self.placement_ptr.y % 2 == 0:
                            # Place row of depots
                            for i in range(self.dimensions.x):
                                x = self.placement_ptr.x
                                y = self.placement_ptr.y

                                self.factory[x][y] = FactoryCell(
                                    depot, -1, -1, -1, -1, Location(x, y), True
                                )
                                self.placement_ptr.x += 1

                            self.placement_ptr.y += 1
                            self.placement_ptr.x = 1

        # Fill the rest of row with depots
        # if(self.placement_ptr.x <= self.dimensions.x):
        while self.placement_ptr.x <= self.dimensions.x:
            x = self.placement_ptr.x
            y = self.placement_ptr.y

            self.factory[x][y] = FactoryCell(
                depot, -1, -1, -1, -1, Location(x, y), True
            )
            self.placement_ptr.x += 1

    def calculatePinRequirements(self):
        for item in self.factory_reqs.keys():
            if item.is_resource:
                # Calculate number of needed pins
                # Pins are shared across partitions
                # Since handled at factory level
                num_pins = 0
                for part in self.partitions.values():
                    # Get the resource requirement for the partition, if exists
                    if not part.part_reqs.get(item) is None:
                        part_resource_rate = part.part_reqs[item]
                        # Determine the needed pins for that requirement
                        if item.is_fluid:
                            num_pins += ceil(part_resource_rate / 25000)
                        else:
                            num_belts = ceil(part_resource_rate / BLUE_BELT)
                            belts_per_car = 2.0

                            num_pins += ceil(
                                num_belts / belts_per_car + self.block_num_buffer
                            )

                            # Don't remember what this was for...
                            # if(num_pins % 2 == 1):
                            #     num_pins += 1

                num_8car_trains = ceil(num_pins / 8)

                self.pin_reqs[item] = num_pins
                template = self.block_templates[item.recipe]
                for _ in range(num_pins):
                    new_block = FactoryBlock(template, self.item_list["research"])
                    self.pin_blocks.append(new_block)

    def placePins(self):
        # Start in top left
        ptr_loc = TOP
        pin_ptr = Location(PIN_CORNER_PADDING, self.dimensions.y + 1)
        for block in self.pin_blocks:
            x = pin_ptr.x
            y = pin_ptr.y
            if self.factory[x][y] == EMPTY:
                block.location = Location(x, y)
                for fcell in block.fcells:
                    fcell.setLocation(block.location)
                    self.factory[fcell.location.x][fcell.location.y] = fcell

                    if ptr_loc == BOT or ptr_loc == RIGHT:
                        fcell.outputs[0].placement = BOT

                # Update pointer
                if ptr_loc == TOP:
                    pin_ptr.x += 1
                    if pin_ptr.x > self.dimensions.x + 1 - PIN_CORNER_PADDING:
                        pin_ptr.y = self.dimensions.y + 1 - PIN_CORNER_PADDING
                        pin_ptr.x = self.dimensions.x + 1
                        ptr_loc = RIGHT
                elif ptr_loc == RIGHT:
                    pin_ptr.y -= 1
                    if pin_ptr.y < PIN_CORNER_PADDING:
                        pin_ptr.y = 0
                        pin_ptr.x = self.dimensions.x + 1 - PIN_CORNER_PADDING
                        ptr_loc = BOT
                elif ptr_loc == BOT:
                    pin_ptr.x -= 1
                    if pin_ptr.x < PIN_CORNER_PADDING:
                        pin_ptr.x = 0
                        pin_ptr.y = PIN_CORNER_PADDING
                        ptr_loc = LEFT
                elif ptr_loc == LEFT:
                    pin_ptr.y += 1
                    if pin_ptr.y > self.dimensions.y + 1 - PIN_CORNER_PADDING:
                        pin_ptr.x = PIN_CORNER_PADDING
                        pin_ptr.y = self.dimensions.y + 1
                        ptr_loc = TOP
            else:
                print("Too many pins for the factory")

    def populateTestFactory(self):
        for x in range(self.dimensions.x + 2):
            for y in range(self.dimensions.y + 2):
                self.tf[x][y] = self.factory[x][y]

    def checkTestFactory(self):
        for x in range(self.dimensions.x):
            for y in range(self.dimensions.y):
                tc = self.tf[x][y]
                ac = self.factory[x][y]
                if tc != ac:
                    return False

        return True

    def validateFactoryCellLocations(self):
        for x in range(1, self.dimensions.x + 1):
            for y in range(1, self.dimensions.y + 1):
                cell = self.factory[x][y]
                if cell.location.x != x or cell.location.y != y:
                    print("factory bad")
                    return False

        return True

    def shufflePins(self):
        print("to do I guess, I'm honestly fine with keeping it as is")

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
                print(
                    "\t"
                    + requester.name
                    + " requests "
                    + str(self.reqs_breakdown[item][requester])
                    + "/min"
                )
