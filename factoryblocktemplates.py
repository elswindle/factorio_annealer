import csv as csv
from globals import *
import item
import recipe


class FactoryBlockTemplate:
    def __init__(self, recipe: recipe.Recipe, csv_reader: csv.reader, item_list):
        # Special case for depots
        if recipe.name == "depot":
            self.recipe = recipe
            return

        self.recipe = recipe
        self.inputs = []  # IOTemplates
        self.outputs = []  # IOTemplates
        self.pcells = []  # Locations

        self.item = 0
        self.direction = 0
        self.placement = 0
        self.rate = 0

        # Get next row of information
        row = next(csv_reader)
        # Iterate until 'end' comes, this means the block template is over
        while row[0] != "end":
            item = item_list[row[1]]  # Retrieve item object
            loc = Location(int(row[2]), int(row[3]))  # Build location
            if row[4] == "TOP":  # Get IO placement (TOP/BOT)
                pm = TOP
            elif row[4] == "BOT":
                pm = BOT
            else:
                print("IO placement is wrong when trying to build cell template")
                pm = -1

            # Add IO
            if row[0] == "ip":
                self.addInput(item, loc, pm)
            elif row[0] == "op":
                self.addOutput(item, loc, pm, row[5])
            else:
                print("Direction is wrong when trying to build IOTemplate")

            row = next(csv_reader)

    def __str__(self):
        ostr = self.recipe.name + "\n"
        ostr += "There are " + str(len(self.inputs)) + " inputs:\n"
        for ip in self.inputs:
            ostr += str(ip) + "\n"

        ostr += "There are " + str(len(self.outputs)) + " outputs:\n"
        for op in self.outputs:
            ostr += str(op) + "\n"

        return ostr

    def __repr__(self):
        return "template " + self.recipe.name

    def addInput(self, item, location, placement):
        if len(self.pcells) == 0:
            self.pcells.append(location)
        else:
            found = False
            for cell in self.pcells:
                if cell == location:
                    found = True

            if not found:
                self.pcells.append(location)

        self.inputs.append(IOTemplate(location, placement, INPUT, item))

    def addOutput(self, item, location, placement, rate):
        # type: (item.Item, Location, int, float) -> None
        if len(self.pcells) == 0:
            self.pcells.append(location)
        else:
            found = False
            for cell in self.pcells:
                if cell == location:
                    found = True

            if not found:
                self.pcells.append(location)

        self.outputs.append(IOTemplate(location, placement, OUTPUT, item, rate))

    def getSize(self):
        return len(self.pcells)


class IOTemplate:
    def __init__(self, location, placement, direction, item, rate=0):
        self.location = location  # (x,y) offset
        self.placement = placement  # TOP/BOT
        self.direction = direction  # INPUT/OUTPUT
        self.item = item  # Item
        self.rate = rate  # Output rate (0 for inputs)

    def __str__(self):
        ostr = self.item.name
        if self.direction == INPUT:
            ostr += " is an input\n"
        else:
            ostr += " is an output with rate of " + str(self.rate) + "\n"
        ostr += "\tLoc: " + str(self.location)
        pstr = ""
        if self.placement == TOP:
            pstr = "TOP"
        else:
            pstr = "BOT"

        ostr += " " + pstr

        return ostr
