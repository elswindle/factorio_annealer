import numpy as np

TOP = 0
BOT = 1
LEFT = 2
RIGHT = 3
INPUT = 0
OUTPUT = 1

class Location:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, comp):
        if(isinstance(comp, Location) and self.x == comp.x and self.y == comp.y):
            return True
        else:
            return False

    def __ne__(self, comp):
        ret = False
        if(isinstance(comp, Location)):
            if(self.x != comp.x or self.y != comp.y):
                ret = True

        return ret
    
    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    def setLocation(self, x, y):
        self.x = x
        self.y = y

class Dimension:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, comp):
        if(isinstance(comp, Dimension) and self.x == comp.x and self.y == comp.y):
            return True
        else:
            return False

    def setDimensions(self, x, y):
        self.x = x
        self.y = y