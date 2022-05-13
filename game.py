import csv as csv
import factory
import item
import recipe

class Game:
    def __init__(self):
        self.factory = 0
        self.item_list = {}
        self.recipe_list = {}

    def loadItemList(self, path):
        item_csv = csv.reader(open(path), delimiter=',')
        next(item_csv)
        for row in item_csv:
            self.item_list[row[0]] = item.Item(row)

    def printItemList(self):
        for item in self.item_list.values():
            print(item)
