TOP = 0
BOT = 1
LEFT = 2
RIGHT = 3
INPUT = 0
OUTPUT = 1
IS_RESOURCE = -1

INITIAL_TEMP = 10000

RIGHT_COST = 0.25
STRAIGHT_COST = 1

# Drawer related
BLOCKX = 20
BLOCKY = 20

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

    def __str__(self):
        return str(self.x) + " x " + str(self.y)

    def setDimensions(self, x, y):
        self.x = x
        self.y = y

def calculateDistanceCost(a : Location, b : Location, bp):
    ax = a.x
    ay = a.y
    bx = b.x
    by = b.y

    # Baseline number of rights is 4
    rights = 4
    straights = abs(bx-ax) + abs(by-ay)
    if(ax > bx): # if destination is to the left
        if(bp == BOT):
            rights += 2
    elif(ax < bx or (ax == bx and ay > by)): # if destination is to the right or directly below
        if(bp == BOT):
            rights -= 2
    else: # if destination is directly above start
        rights -= 4

    return rights*RIGHT_COST + straights*STRAIGHT_COST

# Simple multiplcation is easiest algorithm
# Alternatives could include an exponential for distance
#   where lower distances are slightly more expensive
#   due to acceleration
def calculateTrafficCost(dist, tpm):
    return dist * tpm