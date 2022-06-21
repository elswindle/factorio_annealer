from item import Item
from utils import *


class Recipe:
    def __init__(self, **kwargs):
        # type: (str, **dict) -> None
        if "is_depot" in kwargs:
            self.name = "depot"
            self.item = "dummy"
            return

        if "name" in kwargs:
            self.name = kwargs.pop("name")

        if "energy_required" in kwargs:
            self.craft_time = kwargs.pop("energy_required")
        else:
            self.craft_time = 1

        self.ingredients = {}
        if "ingredients" in kwargs:
            ingredients = kwargs.pop("ingredients")
            for ingredient in ingredients:
                if isinstance(ingredient, list):
                    self.ingredients[ingredient[0]] = ingredient[1]
                elif isinstance(ingredient, dict):
                    self.ingredients[ingredient["name"]] = ingredient["amount"]

        self.products = {}
        if "result" in kwargs:
            self.products[self.name] = 1

        if "results" in kwargs:
            results = kwargs.pop("results")
            for result in results:
                if isinstance(result, list):
                    self.products[result[0]] = result[1]
                elif isinstance(result, dict):
                    self.products[result["name"]] = result["amount"]
                # self.outputs[result[0]] = result[1]

        if "category" in kwargs:
            self.category = kwargs.pop("category")
        else:
            self.category = "assembling-machine"

        self.item = IS_RESOURCE
        if "item" in kwargs:
            self.item = kwargs.pop("item")
            self.item.recipes.append(self)

    def getMaxModules(self):
        mods = 4
        if self.category == "centrifuging":
            mods = 2
        elif self.category == "oil_processing":
            mods = 3
        elif self.category == "chemistry":
            mods = 3
        elif self.category == "smelting":
            mods = 2

        return mods

    def __str__(self):
        recipe_str = self.name + ":\n"
        recipe_str += str(self.craft_time) + " "
        for ingredient in self.ingredients.keys():
            recipe_str += ingredient + " "

        recipe_str += "\n\t-> "
        for product in self.products.keys():
            recipe_str += product + " "

        return recipe_str

    def __repr__(self):
        return self.name + " recipe"
