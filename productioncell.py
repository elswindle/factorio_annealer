from globals import *
import factorycellio
# prod_cell
#   ios
#       inputs
#           item, rate, loc, Location, FactoryCell
#       outputs
#           item, rate, loc, Location, FactoryCell

class ProductionCell:
    def __init__(self, offset: Location, ios):
        self.offset = offset
        in_data = ios[0]
        out_data = ios[1]

        fcell_ios = []
        for i in in_data:
            io_data = in_data[i]
            fcell_ios.append(factorycellio(io_data))
