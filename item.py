from globals import IS_RESOURCE

class Item:
    def __init__(self, row):
        self.name = row[0]
        self.stack_size = int(row[1])
        if(row[2] == 'Yes'):
            self.is_fluid = True
        elif(row[2] == 'No'):
            self.is_fluid = False
        else:
            self.is_fluid = -1
            print("Issue with reading item reader, is fluid not specified correctly for item")
            print(self.name)

        if(row[3] == 'Yes'):
            self.is_resource = True
        elif(row[3] == 'No'):
            self.is_resource = False
        else:
            self.is_resource = -1
            print("Issue with reading item reader, resource not specified")
            print(self.name)
            
        self.is_producer = []
        self.is_requester = []

        self.routes_to = {}
        self.routes_from = {}

        self.recipe = IS_RESOURCE

    def __str__(self):
        item_str = self.name + ", stack size=" + str(self.stack_size)
        fluid_str = "is "
        if(self.is_fluid == False):
            fluid_str += "not "

        fluid_str += "a fluid"
        item_str += ", " + fluid_str
        return item_str

    def __repr__(self):
        return self.name + " item"

    # def __eq__(self, comp):
    #     if(self.name == comp.name):
    #         return True
    #     else:
    #         return False

    # def __ne__(self, comp):
    #     return not(self == comp)

    def printProducers(self):
        print("producers...")

    def printRequesters(self):
        print("requesters...")

    def printRoutesToItem(self):
        print("routes to...")

    def printRoutesFromItem(self):
        print("routes from...")

    def addRouteToItem(self, item):
        if(self.routes_to.has_key(item)):
            self.routes_to[item] += 1
        else:
            print("new route to")
            self.routes_to[item] = 1

    def addRouteFromItem(self, item):
        if(self.routes_from.has_key(item)):
            self.routes_from[item] += 1
        else:
            print("new route from")
            self.routes_from[item] = 1

    def addProducer(self, cell_io):
        self.is_producer.append(cell_io)

    def addRequester(self, cell_io):
        self.is_requester.append(cell_io)

    def addRecipe(self, recipe):
        self.recipe = recipe