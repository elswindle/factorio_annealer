from utils import *

if TYPE_CHECKING:
    from recipe import Recipe
    from factorycellio import FactoryCellIO


class Item:
    def __init__(self, **kwargs):
        # type: (**dict) -> None
        from_game_data = True
        if "row" in kwargs:
            from_game_data = False
            row = kwargs.pop("row").split(",")

        if not from_game_data:
            self.name = row[0]
            self.stack_size = int(row[1])
            if row[2] == "Yes":
                self.is_fluid = True
            elif row[2] == "No":
                self.is_fluid = False
            else:
                self.is_fluid = -1
                print(
                    "Issue with reading item reader, is fluid not specified correctly for item"
                )
                print(self.name)

            if row[3] == "Yes":
                self.is_resource = True
            elif row[3] == "No":
                self.is_resource = False
            else:
                self.is_resource = -1
                print("Issue with reading item reader, resource not specified")
                print(self.name)
        else:
            self.is_fluid = False
            self.is_resource = False

            if "name" in kwargs:
                self.name = kwargs.pop("name")

            if "stack_size" in kwargs:
                self.stack_size = kwargs.pop("stack_size")

            if "type" in kwargs:
                item_type = kwargs.pop("type")
                if item_type == "fluid":
                    self.is_fluid = True
                    self.stack_size = 25000

            if "subgroup" in kwargs:
                subgroup = kwargs.pop("subgroup")
                if subgroup == "raw-resource":
                    self.is_resource = True

            # Manually add fluid raw-resources
            if self.name in ["crude-oil", "water"]:
                self.is_resource = True

        self.is_producer = []  # type: list[FactoryCellIO]
        self.is_requester = []  # type: list[FactoryCellIO]

        self.routes_to = {}
        self.routes_from = {}

        self.preferred_recipe = None
        self.recipes = []  # type: list[Recipe]

    def setPreferredRecipe(self, recipe):
        # type: (Recipe) -> None
        if recipe in self.recipes:
            for rec in self.recipes:
                recipe.is_preferred = False

            recipe.is_preferred = True
            self.preferred_recipe = recipe
        else:
            raise AttributeError("Recipe not in recipe list")

    def __str__(self):
        item_str = self.name + ", stack size=" + str(self.stack_size)
        fluid_str = "is "
        if self.is_fluid == False:
            fluid_str += "not "

        fluid_str += "a fluid"
        item_str += ", " + fluid_str
        return item_str

    def __repr__(self):
        return self.name + " item"

    # def __eq__(self, comp):
    #     if(self.name == comp.name):
    #         return True
    #     else:
    #         return False

    # def __ne__(self, comp):
    #     return not(self == comp)

    def printProducers(self):
        print("producers...")

    def printRequesters(self):
        print("requesters...")

    def printRoutesToItem(self):
        print("routes to...")

    def printRoutesFromItem(self):
        print("routes from...")

    def addRouteToItem(self, item):
        # type: (Item) -> None
        if self.routes_to.has_key(item):
            self.routes_to[item] += 1
        else:
            print("new route to")
            self.routes_to[item] = 1

    def addRouteFromItem(self, item):
        # type: (Item) -> None
        if self.routes_from.has_key(item):
            self.routes_from[item] += 1
        else:
            print("new route from")
            self.routes_from[item] = 1

    def addProducer(self, cell_io):
        # type: (FactoryCellIO) -> None
        self.is_producer.append(cell_io)

    def addRequester(self, cell_io):
        # type: (FactoryCellIO) -> None
        self.is_requester.append(cell_io)

    def addRecipe(self, recipe, is_preferred=False):
        # type: (Recipe, bool) -> None
        if recipe not in self.recipes:
            self.recipes.append(recipe)
            recipe.is_preferred = is_preferred
            if is_preferred:
                self.preferred_recipe = recipe
        else:
            raise AttributeError("Recipe already in item's recipe list")
