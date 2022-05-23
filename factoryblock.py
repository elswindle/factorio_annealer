import factorycell
from globals import *
import factorycellio

class FactoryBlock:
    def __init__(self, template, part_top):
        self.recipe = -1
        self.inputs = []
        self.outputs = []
        self.fcells = []            # FactoryCell
        self.location = -1
        self.dimension = -1         # Simplify block placement
        self.num_left = 0           # Simplify block placement
        self.num_below = 0          # Simplify block placement

        if(template != IS_RESOURCE):
            self.recipe = template.recipe
            self.part_top = part_top

            # Find size and orientation of FactoryCells
            minx = 0
            maxx = 0
            miny = 0
            maxy = 0
            for pcell in template.pcells:
                if(pcell.x < minx):
                    minx = pcell.x
                if(pcell.x > maxx):
                    maxx = pcell.x
                if(pcell.y < miny):
                    miny = pcell.y
                if(pcell.y > maxy):
                    maxy = pcell.y

            self.num_left = abs(minx)
            self.num_below = abs(miny)
            self.dimension = Dimension(maxx-minx+1,maxy-miny+1)

            # Build arrays of i/ps and o/ps
            ips = []*len(template.pcells)
            ops = []*len(template.pcells)

            for iotemp in template.inputs:
                ioloc = iotemp.location
                # find template location
                idx = 0
                for pcell in range(len(template.pcells)):
                    if(template.pcells[pcell] == ioloc):
                        idx = pcell
                
                ips.append(iotemp)

            for iotemp in template.outputs:
                ioloc = iotemp.location
                # find template location
                idx = 0
                for pcell in range(len(template.pcells)):
                    if(template.pcells[pcell] == ioloc):
                        idx = pcell
                
                ops.append(iotemp)

            for offset in template.pcells:
                self.fcells.append(factorycell.FactoryCell(template, part_top, ips, ops, offset))

    def __repr__(self):
        return self.recipe.name + " block"