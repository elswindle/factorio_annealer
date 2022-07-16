from item import Item
from utils import *

class Recipe:
    def __init__(self, **kwargs):
        # type: (str, **dict) -> None
        if "is_depot" in kwargs:
            self.name = "depot"
            self.item = "dummy"
            return

        self.craft_time = 1

        if "name" in kwargs:
            self.name = kwargs.pop("name")

        if "energy_required" in kwargs:
            self.craft_time = kwargs.pop("energy_required")

        found_ing = False
        found_res = False
        self.ingredients = {}  # type: Mapping[str, float]
        self.products = {}  # type: Mapping[str, float]
        if "normal" in kwargs:
            norm_settings = kwargs.pop("normal")
            if "ingredients" in norm_settings:
                ingredients = norm_settings["ingredients"]
                found_ing = True
            if "result" in norm_settings:
                self.products[self.name] = 1

            if "results" in norm_settings:
                results = norm_settings["results"]
                found_res = True

            if "energy_required" in norm_settings:
                self.craft_time = norm_settings.pop("energy_required")

        if "ingredients" in kwargs:
            ingredients = kwargs.pop("ingredients")
            found_ing = True

        if found_ing:
            for ingredient in ingredients:
                if isinstance(ingredient, list):
                    self.ingredients[ingredient[0]] = ingredient[1]
                elif isinstance(ingredient, dict):
                    self.ingredients[ingredient["name"]] = ingredient["amount"]

        if "result" in kwargs:
            self.products[self.name] = 1

        if "result_count" in kwargs:
            self.products[self.name] = kwargs["result_count"]

        if "results" in kwargs:
            results = kwargs.pop("results")
            found_res = True

        if found_res:
            for result in results:
                if isinstance(result, list):
                    self.products[result[0]] = result[1]
                elif isinstance(result, dict):
                    self.products[result["name"]] = result["amount"]

        if "category" in kwargs:
            self.category = kwargs.pop("category")
        else:
            self.category = "assembling-machine"

        self.item = None # type: Item
        if "item" in kwargs:
            self.item = kwargs.pop("item")
            self.item.recipes.append(self)

        if "preferred" in kwargs:
            self.is_preferred = kwargs.pop("perferred")
        else:
            self.is_preferred = False

    def getMaxModules(self):
        mods = 4
        if self.category == "centrifuging":
            mods = 2
        elif self.category == "oil-processing":
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
