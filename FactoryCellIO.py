import Item
from globals import *

class FactoryCellIO:
    def __init__(self, item: Item, rate, direction):
        self.item = item
        self.rate = rate
        self.direction = direction