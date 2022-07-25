from factorycellio import FactoryCellIO
from factoryblocktemplates import FactoryBlockTemplate
from factorycell import FactoryCell
from factoryblock import FactoryBlock
from numpy import isin
from recipe import Recipe
from item import Item
from partition import Partition
from customlists import PartitionDict
from utils import *
from math import ceil, floor, sqrt
import factorycalculator as calculator
import csv as csv


class Factory:
    def __init__(self, **kwargs):
        """
        Factory initialization, arguments contain different options for calculation,
        top level items.  Loads item and recipe lists from game data if not
        specified in arguments
        :param kwargs: Available factory options
            "top-items" : Top level item names and production rates for the
            factory to produce.  These cannot be a dependency of each other or
            of any of the top level items of the partitions.  Assignment and
            addition will check ensure this criteria is met.
            "depot-adjacency-requirement" : Factory layout requirement for the
            number of LTN depots adjacent to each FactoryCell.  Default is 2, maximum
            is 6.
            "productivity-bonus" : Productivity bonus from a single module.
            Vanilla bonuses are in [0, 0.04, 0.06, 0.1], default is prod-3 (0.1)
            "calc-exceptions" : List of solids/fluids to be handled differently
            when calculating the factory requirements.  These will generally be
            items that can be produced via multiple recipes.  For vanilla Factorio,
            this includes oil products, i.e. light oil and petroleum.  Default items
            are heavy oil, light oil and petroluem gas.
            "partitions" : List of all item names as top level partitions.  A partition
            is defined as a set of factory blocks that produce the resources needed to
            create the top item.  The size and requirements for these partitions are
            calculated based on the desired rate of the factory's top level items
            defined in "top-items".
            "block-template-path" : Custom list of all block templates to be used
            in the factory.  For any partition, all sub-recipes must be defined
            within the given file.
            "use-unique-network" : Boolean specifying if the LTN train stations
            should operate using unique network ids.  This means blocks within a
            partition will only service blocks within the partition unless the item
            is the top item in a partition.  For example, if advanced circuits
            have their own partition, those factory blocks will have to be assigned
            to the advanced circuit partition blocks to get the needed resources
            and also assigned to any other partition network that uses them, i.e.
            chemical science packs.
        """
        # type: (float, **dict) -> None

        self.pin_reqs = {}  # type: Mapping[Item, int] # Resource, num_pins
        self.pin_blocks = []  # type: list[FactoryBlock]

        if "depot-adjacency-requirement" in kwargs:
            self.depot_req = kwargs.pop("depot-adjacency-requirement")
        else:
            self.depot_req = 2

        self.block_templates = {}  # type: Mapping[Recipe, FactoryBlockTemplate]
        self.recipe_list = {}  # type: Mapping[str, Recipe]
        self.item_list = {}  # type: Mapping[str, Item]

        self.block_num_buffer = 0.1
        self.depot_ratio = 1 / 4
        self.dimensions = -1
        # Factory and test factory, FactoryCell[x][y]
        self.factory = None  # type: list[list[FactoryCell]]
        self.tf = None  # type: list[list[FactoryCell]]
        self.prod_limitations = (
            []
        )  # type: list[str] # Specifies which recipes can use productivity modules
        self.placement_ptr = Location(
            1, 1
        )  # keeps track of location to place next block

        # Load calculation options
        if "productivity-bonus" in kwargs:
            self.prod_bonus = kwargs.pop("productivity-bonus")
        else:
            self.prod_bonus = 0.1

        if "calc-exceptions" in kwargs:
            self.calc_exceptions = kwargs.pop("calc-exceptions")
        else:
            self.calc_exceptions = []

        if "item_list_path" in kwargs:
            # type: (str) -> None
            self.item_list_path = kwargs.pop("item_list_path")
            item_csv = csv.reader(open(self.item_list_path), delimiter=",")
            next(item_csv)
            for row in item_csv:
                self.item_list[row[0]] = Item(**{"row": row})
        else:
            self.loadItemsFromGameData()

        self.top_items = {}  # type: Mapping[Item, float]
        if "top-items" in kwargs:
            top = kwargs.pop("top-items")
            for item_data in top:
                item = self.item_list[item_data[0]]
                self.top_items[item] = item_data[1]

        self.loadRecipesFromGameData()

        if "block-template-path" in kwargs:
            self.template_path = kwargs.pop("block-template-path")
            self.importBlockTemplates(self.template_path)
            self.overrideRecipes()

        if "partitions" in kwargs:
            part_names = kwargs.pop("partitions")
        else:
            part_names = []

        parts = []
        for name in part_names:
            parts.append(self.item_list[name])
        self.partitions = PartitionDict(self, parts)  # type: Mapping[Item, Partition]
        next_id = len(self.partitions)
        for i, item in enumerate(self.top_items.keys()):
            self.partitions[item] = Partition(
                item, next_id + i, main=True, rate=self.top_items[item]
            )

        self.unique_networks = False
        if "use-unique-network" in kwargs:
            self.unique_networks = kwargs.pop("use-unique-network")

        for arg in kwargs:
            print(arg)

    def loadItemsFromGameData(self):
        """
        Loads list of Item objects from Factorio game data.  This function is jank,
        it basically just hacks item.lua and fluid.lua and removes any references
        to functions or data structures defined by the game outside of the file.
        Ideally, this will be getting data from loaded Factorio data through Lua.
        In addition, this can be expanded to include mods and can build a layout
        from modded data.
        """
        try:
            solids_file = open("factorio-data/base/prototypes/item.lua", "r")
        except:
            print(
                "Unable to load solids file from game data, ensure factorio-data is populated"
            )
        try:
            fluid_file = open("factorio-data/base/prototypes/fluid.lua", "r")
        except:
            print(
                "Unable to load fluids file from game data, ensure factorio-data is populated"
            )

        next(solids_file)
        next(solids_file)
        next(solids_file)
        next(solids_file)
        next(solids_file)

        # Load productivity module limitations
        prod_str = ""
        line = solids_file.readline()
        while line.find("}") == -1:
            prod_str += line
            line = solids_file.readline()

        # Remove new lines, quotes and spaces
        prod_str = prod_str.replace("\n", "")
        prod_str = prod_str.replace(" ", "")
        prod_str = prod_str.replace('"', "")
        self.prod_limitations = prod_str.split(",")

        # Load solids
        # get to the solids data section
        line = solids_file.readline()
        while line != "data:extend(\n":
            line = solids_file.readline()

        item_str = ""
        line = solids_file.readline()
        while line != ")\n":
            add = True
            if line.find("sounds") != -1:
                line = line.replace("sounds.", '"')
                line = line.replace("\n", '"\n')

            if line.find("require(") != -1 or line.find("limitation()") != -1:
                add = False

            if add:
                item_str += line

            line = solids_file.readline()
        # item_str = item_str[: len(item_str) - 2]  # Throw away final ")"
        item_table = lua.eval(item_str)
        solids = convert_table_to_dict(item_table)

        # Load fluids
        next(fluid_file)
        fluid_str = fluid_file.read()
        fluid_str = fluid_str[: len(fluid_str) - 2]
        fluid_table = lua.eval(fluid_str)
        fluids = convert_table_to_dict(fluid_table)

        # Compile all dict entries into Item objects and add to item_list
        for solid in solids:
            self.item_list[solid["name"]] = Item(**solid)

        for fluid in fluids:
            self.item_list[fluid["name"]] = Item(**fluid)

        # Add custom items, these are "fake" items to represent performing research
        # Enables consuming science packs and gives raw resources to consume something
        self.item_list["labs"] = Item(
            **{"row": "labs,1000,No,No"}
        )  # item that consumes all science packs
        self.item_list["research"] = Item(
            **{"row": "research,10000000,No,No"}
        )  # Parent item for labs
        self.item_list["miner"] = Item(
            **{"row": "miner,1,No,No"}
        )  # raw-resources consume this

    def loadRecipesFromGameData(self):
        with open("factorio-data/base/prototypes/recipe.lua", "r") as file:
            next(file)
            recipe_str = file.read()
            recipe_str = recipe_str[: len(recipe_str) - 2]
            recipe_table = lua.eval(recipe_str)
            recipes = convert_table_to_dict(recipe_table)

            for recipe in recipes:
                # if recipe["name"] == "rocket_part":
                #     recipe["name"] = "space-science-pack"
                #     recipe["result"] = "space-science-pack"
                recipe["item"] = self.getRecipeItem(recipe["name"])
                self.recipe_list[recipe["name"]] = Recipe(**recipe)

            # Custom recipes for non-standard products
            # This includes science pack consumption, research
            # space-science packs and resources
            lab_dict = {
                "name": "labs",
                "ingredients": [
                    ["automation-science-pack", 1],
                    ["logistic-science-pack", 1],
                    ["military-science-pack", 1],
                    ["chemical-science-pack", 1],
                    ["production-science-pack", 1],
                    ["utility-science-pack", 1],
                    ["space-science-pack", 1],
                ],
                "result": "labs",
                "item": self.item_list["labs"],
            }
            self.recipe_list["labs"] = Recipe(**lab_dict)

            research_dict = {
                "name": "research",
                "ingredients": [["labs", 1]],
                "result": "research",
                "item": self.item_list["research"],
            }
            self.recipe_list["research"] = Recipe(**research_dict)

            # Gives a recipe for space science
            space_dict = {
                "name": "space-science-pack",
                "ingredients": [["rocket-part", 100], ["satellite", 1]],
                "results": [["space-science-pack", 1000]],
                "item": self.item_list["space-science-pack"],
            }
            self.recipe_list["space-science-pack"] = Recipe(**space_dict)

            # Placeholder recipe for resources, helps with recursion
            for item in self.item_list.values():
                if item.is_resource or item.name in ["crude-oil", "water"]:
                    r_dict = {
                        "name": item.name,
                        "ingredients": [["miner", 1]],
                        "result": item.name,
                        "item": item,
                    }
                    self.recipe_list[item.name] = Recipe(**r_dict)

            # Make sure every item has a preferred recipe if one is available
            for item in self.item_list.values():
                if len(item.recipes) != 0:
                    item.setPreferredRecipe(item.recipes[0])

                    # Exceptions
                    if item.name == "petroleum-gas":
                        item.setPreferredRecipe(self.recipe_list["light-oil-cracking"])
                    elif item.name == "light-oil":
                        item.setPreferredRecipe(self.recipe_list["heavy-oil-cracking"])
                    elif item.name == "heavy-oil":
                        item.setPreferredRecipe(
                            self.recipe_list["advanced-oil-processing"]
                        )
                    elif item.name == "solid-fuel":
                        item.setPreferredRecipe(
                            self.recipe_list["solid-fuel-from-light-oil"]
                        )

    def loadFactoryRecipeList(self, path):
        # type: (str, bool) -> None
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

            item = self.getRecipeItem(recipe_name)
            recipe_dict = {
                "name": recipe_name,
                "ingredients": inputs,
                "results": outputs,
                "energy_required": craft_time,
                "item": item,
            }
            new_recipe = Recipe(**recipe_dict)
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

    def overrideRecipes(self):
        # Go over block templates and modify game data recipes to
        # match ones given by the template
        # This function requires items to be exclusively produced 
        # either locally or in their own template.  It can't have both
        for recipe in self.block_templates:
            template = self.block_templates[recipe]

            # For any recipe that is not a resource
            if not recipe.item.is_resource:
                # Keep track of items to remove or add to a recipe
                items_to_add = []
                items_to_remove = []

                # Iterate on the recipe's ingredients
                for ingredient_name in recipe.ingredients:
                    ingredient = self.item_list[ingredient_name]
                    item = self.getRecipeItem(recipe.name)
                    ingredient_amt = recipe.ingredients[ingredient_name]

                    # If the recipe's ingredient doesn't have a template, search
                    # it's ingredients for templates
                    if self.block_templates.get(ingredient.preferred_recipe) is None:
                        # Keep track of the which items need to be added to the recipe
                        items_to_add += self.templateRecursiveSearch(
                            ingredient.preferred_recipe, ingredient_amt, ingredient
                        )
                        # Any item that doesn't have a template is marked for removal
                        items_to_remove.append(ingredient_name)

                # Perform removal/addition of items to recipe
                for item in items_to_remove:
                    recipe.ingredients.pop(item)
                for item in items_to_add:
                    if recipe.ingredients.get(item[0]) is None:
                        recipe.ingredients[item[0]] = item[1]
                    else:
                        recipe.ingredients[item[0]] += item[1]

    def templateRecursiveSearch(self, recipe, craft_amt, product):
        # type: (Recipe, float, Item) -> list
        # Recursively search recipes of a given ingredient for recipes
        # that have templates
        items_to_add = []
        for ingredient_name in recipe.ingredients:
            # Since item is produced locally, the factory calculator
            # will not take productivity into consideration, so it must
            # be done here
            productivity = 1
            if recipe.name in self.prod_limitations:
                productivity = 1 + recipe.getMaxModules() * self.prod_bonus
            ingredient = self.item_list[ingredient_name]
            # Keep track of the amount of each item that is needed in order
            # for the calculator to produce correct results
            ingredient_amt = (
                craft_amt
                * recipe.ingredients[ingredient_name]
                / (productivity * recipe.products[product.name])
            )

            # Continue the recursion if the current recipe does not have a template
            if self.block_templates.get(ingredient.preferred_recipe) is None:
                items_to_add += self.templateRecursiveSearch(
                    ingredient.preferred_recipe, ingredient_amt, ingredient
                )
            else:
                items_to_add.append((ingredient_name, ingredient_amt))

        return items_to_add

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

    def calculateFactoryRequirements(self):
        for partition in self.partitions.values():
            partition.calculateNormalizedPartitionRequirements(self)

        scalars = {}
        for part in self.partitions.values():
            if part.main:
                self.getPartitionScalars(part, 0, [part])
                scalars[part] = 0

    def getPartitionScalars(self, partition, scalar, visited):
        # type: (Partition, float, list[Partition]) -> None
        partition.partition_scalar += scalar
        for part in self.partitions.values():
            try:
                part_scalar = partition.part_reqs[part.top_item]
            except:
                part_scalar = 0

            part_scalar *= partition.partition_scalar

            if part != partition and part_scalar != 0:
                if part not in visited:
                    self.getPartitionScalars(part, part_scalar, [part] + visited)
                else:
                    raise BaseException(
                        "Circular dependecy detected, partition already visited\n"
                        + "Partition: "
                        + str(part)
                        + "\n"
                        + str(visited)
                    )

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

    def populateFactory(self):
        for part in self.partitions.values():
            part.populateFactoryBlocks(self)

        if self.unique_networks:
            self.setNetworkIDs()

    def setNetworkIDs(self):
        for partition in self.partitions.values():
            for item in partition.part_reqs.keys():
                # Handle top partition items differently since
                # factory blocks are not stored within this partition
                if item in self.partitions.keys() and item != partition.top_item:
                    # For top level items, go into partition and iterate on
                    # blocks that match item's recipe and add current partition's
                    # id to the block's ID
                    for block in self.partitions[item].factory_blocks:
                        if block.recipe in item.recipes:
                            block.network_id += pow(2,partition.id)

            # For non top level items, assign all factory blocks
            # to the current partition's ID
            for block in partition.factory_blocks:
                block.network_id += pow(2,partition.id)

    def initializeBlockPlacement(self):
        self.num_cells = self.getFactoryCellAmount()
        self.num_blocks = self.getFactoryBlockAmount()

        depot = FactoryBlockTemplate(Recipe(**{"is_depot": True}), -1, -1)
        placed_blocks = 0
        for part in self.partitions.values():
            factory_blocks = part.factory_blocks
            for block in factory_blocks:
                # Make sure block can fit in available location
                # Check for different sized blocks
                anchor = Location(block.num_left, block.num_below)
                if block.dimension != Dimension(1, 1):
                    # Check if block will fit in current location
                    space_left = self.dimensions.x - self.placement_ptr.x + 1
                    if space_left < block.dimension.x:
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
        # Go through all items
        for item in self.item_list.values():
            # For any item that is marked as a resource and has a block
            # template, calculate the number of pins required
            if (
                item.is_resource
                and self.block_templates.get(item.preferred_recipe) is not None
            ):
                num_pins = 0
                # Iterate over partitions and factory top items
                for part in self.partitions.values():
                    # Get the correct requirements dictionary
                    reqs = part.part_reqs

                    # Check if the item is required
                    if reqs.get(item) is not None:
                        resource_rate = reqs[item] * part.partition_scalar

                        # Determine number of pins based on the resource type
                        if item.is_fluid:
                            num_pins += ceil(resource_rate / 25000)
                        else:
                            num_belts = ceil(resource_rate / BLUE_BELT)
                            belts_per_car = 2.0

                            num_pins += ceil(
                                self.block_num_buffer + (num_belts / belts_per_car)
                            )

                num_8car_trains = ceil(num_pins / 8)

                # Store the number of pins and create the factory block
                self.pin_reqs[item] = num_pins
                template = self.block_templates[item.preferred_recipe]

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

    def addFluidDepots(self):
        fluid_recipes = []
        for recipe in self.recipe_list.values():
            requires_fluid = False
            for ingredient in recipe.ingredients.keys():
                if self.item_list[ingredient].is_fluid:
                    requires_fluid = True
                    break

            if requires_fluid:
                fluid_recipes.append(recipe)

        for x in range(self.dimensions.x + 2):
            for y in range(self.dimensions.y + 2):
                cell = self.factory[x][y]
                if cell is not EMPTY:
                    if cell.recipe in fluid_recipes:
                        # Replace one depot with a fluid depot
                        replaced = False
                        for xoff in range(-1, 2):
                            for yoff in range(-1,2):
                                if xoff != 0 or y != 0:
                                    neighbor = self.factory[x+xoff][y+yoff]
                                    if neighbor is not EMPTY:
                                        if neighbor.is_depot:
                                            neighbor.is_fluid = True
                                            replaced = True
                                            break
                            if replaced:
                                break

        ns = 0
        nf = 0
        for x in range(self.dimensions.x + 2):
            for y in range(self.dimensions.y + 2):
                cell = self.factory[x][y]
                if cell is not EMPTY:
                    if cell.is_depot:
                        if cell.is_fluid:
                            nf +=1
                        else:
                            ns += 1

        print(nf)
        print(ns)

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

    def getRecipeItem(self, name):
        # type: (str) -> Item
        if name == "advanced-oil-processing" or name == "coal-liquefaction":
            item = self.item_list["heavy-oil"]
        elif name == "heavy-oil-cracking":
            item = self.item_list["light-oil"]
        elif name == "light-oil-cracking" or name == "basic-oil-processing":
            item = self.item_list["petroleum-gas"]
        elif name.find("solid-fuel") != -1:
            item = self.item_list["solid-fuel"]
        elif name == "uranium-processing" or name == "nuclear-fuel-reprocessing":
            item = self.item_list["uranium-238"]
        elif name == "kovarex-enrichment-process":
            item = self.item_list["uranium-235"]
        else:
            item = self.item_list[name]

        return item

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
