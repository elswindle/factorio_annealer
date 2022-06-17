import csv as csv
from factory import Factory
from item import Item
from recipe import Recipe


class Game:
    def __init__(self):
        self.factory = 0
        self.item_list = {}  # {str : Item}
        self.recipe_list = {}

    def loadItemList(self, path):
        # type: (str) -> None
        item_csv = csv.reader(open(path), delimiter=",")
        next(item_csv)
        for row in item_csv:
            self.item_list[row[0]] = Item(row)

    def printItemList(self):
        for item in self.item_list.values():
            print(item)
