TOP = 0
BOT = 1
LEFT = 2
RIGHT = 3
INPUT = 0
OUTPUT = 1
IS_RESOURCE = -1
EMPTY = -1
NOT_FOUND = -1
BLUE_BELT = 2700
PIN_CORNER_PADDING = 2

INITIAL_TEMP = 10000
DEPOT_REQ = 2

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
       return not self == comp

    def __add__(self, add):
        return Location(self.x+add.x, self.y+add.y)
        self.x += add.x
        self.y += add.y

        return self

    def __sub__(self, sub):
        return Location(self.x-sub.x, self.y-sub.y)
        self.x -= sub.x
        self.y -= sub.y

        return self
    
    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    def __repr__(self):
        return str(self)

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

    def __repr__(self):
        return str(self)

    def setDimensions(self, x, y):
        self.x = x
        self.y = y

def calculateDistanceCost(a : Location, b : Location, op, dp):
    ax = a.x
    ay = a.y
    bx = b.x
    by = b.y

    rights  = 4
    straights = abs(bx-ax) + abs(by-ay)
    # Baseline number of rights is 4
    if(op == BOT):
        if(ax > bx): # if destination is to the left
            if(dp == BOT):
                rights += 2
        elif(ax < bx or (ax == bx and ay > by)): # if destination is to the right or directly below
            if(dp == BOT):
                rights -= 2
        else: # if destination is directly above start
            rights -= 4
            if(dp == BOT):
                rights += 2
    elif(op == TOP):
        if(ax > bx or (ax == bx and ay < by)):
            if(dp == TOP):
                rights -= 2
        elif(ax < bx):
            if(dp == TOP):
                rights += 2
        else: # if destination is directly below start
            rights -= 4
            if(dp == TOP):
                rights += 2

    return rights*RIGHT_COST + straights*STRAIGHT_COST

# Simple multiplcation is easiest algorithm
# Alternatives could include an exponential for distance
#   where lower distances are slightly more expensive
#   due to acceleration
def calculateTrafficCost(dist, tpm):
    return dist * tpm

def findFirstInstance(list, obj):
    idx = NOT_FOUND
    for i in range(len(list)):
        if(list[i] == obj):
            idx = i
            break

    return idx

def validLocations(loc_list, factory):
    for loc in loc_list:
        if(loc.x < 1 or loc.x > factory.dimension.x):
            return False
        if(loc.y < 1 or loc.y > factory.dimension.y):
            return False

    return True