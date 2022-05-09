import Item
import ProductionCell

class FactoryBlockTemplate:
    def __init__(self, id, item : Item, type, prod_cell_loc, ios, icon_path):
        self.id = id
        self.item = item
        self.type = type
        self.inputs = []
        self.outputs = []
        self.icon_path = icon_path

        self.pcells = []
        
        for i in len(prod_cell_loc):
            self.pcells.append(ProductionCell(prod_cell_loc[i], ios[i]))

    