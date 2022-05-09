from numpy import true_divide


TOP = 0
BOT = 1
LEFT = 2
RIGHT = 3

class Location:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, comp):
        if(isinstance(comp, Location) and self.x == comp.x and self.y == comp.y):
            return True
        else:
            return False

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