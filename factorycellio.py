import item
from globals import *

class FactoryCellIO:
    def __init__(self, item: item, rate, direction):
        self.item = item
        self.rate = rate
        self.direction = direction
