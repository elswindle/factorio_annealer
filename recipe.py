from item import Item

class Recipe:
    def __init__(self, ct, ips, ops):
        self.craft_time = ct
        self.inputs = ips                   # array of Items
        self.outputs = ops                  # array of Items
        self.item : Item = ops[0]

        # Recipe name exceptions
        if(self.item.name == 'heavy-oil'):
            self.name = 'advanced-oil-processing'
        elif(self.item.name == 'light-oil'):
            self.name = 'heavy-oil-cracking'
        elif(self.item.name == 'petroleum-gas'):
            self.name = 'light-oil-cracking'
        else:
            self.name = self.item.name

    def __str__(self):
        recipe_str = self.name + ":\n"
        recipe_str += str(self.craft_time) + " "
        for input in self.inputs:
            recipe_str += input.name + " "

        recipe_str += "\n\t-> "
        for output in self.outputs:
            recipe_str += output.name + " "

        return recipe_str