import factory
import factorycell
import factorycellio
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.offsetbox as ob
from PIL import Image
from globals import *

class FactoryDrawer:
    def __init__(self, factory : factory.Factory):
        self.factory = factory

    def drawFactory(self):
        # Draw grid
        rows = self.factory.dimensions.y+2
        cols = self.factory.dimensions.x+2
        # Draw bottom and left line
        ymax = rows*BLOCKY
        xmax = cols*BLOCKX
        fig, ax = plt.subplots(1,1,figsize=(xmax/10,ymax/10))
        fig.dpi = 20
        plt.plot([0,xmax],[ymax]*2,color='k')
        plt.plot([xmax]*2,[0,ymax],color='k')

        for row in range(rows):
            plt.plot([0,xmax],[row*BLOCKY]*2,color='k')
        for col in range(cols):
            plt.plot([col*BLOCKX]*2, [0,ymax],color='k')
        
        # Add cell icons
        for row in range(rows):
            for col in range(cols):
                cell = self.factory.factory[col][row]
                if(cell != EMPTY):
                    if(cell.recipe != -1):
                        self.plotIcon(row,col,cell.recipe,ax)

                        # ips = cell.inputs
                        # ops = cell.outputs
                        # for ip in range(len(ips)):
                        #     self.plotIOIcon(row, col, ips[ip].item, ips[ip].placement, ip, len(ips), ax)

                        # for op in range(len(ops)):
                        #     self.plotIOIcon(row, col, ops[op].item, ops[op].placement, op, len(ops), ax)

        # Add cell IO icons (optional)

        # plt.show()

    def circleGroup(self, cell_group, c='r'):
        if(cell_group[0].parent_block == -1):
            base_loc = cell_group[0].location
        else:
            base_loc = cell_group[0].parent_block.location

        lw = 10

        # Find bounding box of group
        left = right = base_loc.x
        top = bot = base_loc.y
        for cell in cell_group:
            if(cell.location.x < left):
                left = cell.location.x
            if(cell.location.x > right):
                right = cell.location.x
            if(cell.location.y < bot):
                bot = cell.location.y
            if(cell.location.y > top):
                top = cell.location.y

        top += 1
        right += 1
        # Scale coordinates
        left *= BLOCKX
        right *= BLOCKX
        top *= BLOCKY
        bot *= BLOCKY
        # Plot 4 lines
        plt.plot([left,right],[bot,bot],color=c, linewidth=lw)
        plt.plot([left,right],[top,top],color=c, linewidth=lw)
        plt.plot([left,left],[bot,top],color=c, linewidth=lw)
        plt.plot([right,right],[bot,top],color=c, linewidth=lw)

    def plotIcon(self, row, col, recipe, ax):
        im_path = 'imgs/' + recipe.name + '.png'

        icon = Image.open(im_path)
        
        xoffset = col*BLOCKX+BLOCKX/2
        yoffset = row*BLOCKY+BLOCKY/2

        imagebox = ob.OffsetImage(icon, zoom=1)
        ab = ob.AnnotationBbox(imagebox, (xoffset,yoffset), frameon=False)

        ax.add_artist(ab)

    def plotIOIcon(self, row, col, item, placement, idx, total, ax):
        # WIP do x offset
        im_path = 'imgs/' + item.name + '.png'
        icon = Image.open(im_path)
        xoffset = col*BLOCKX+BLOCKX/2
        yoffset = row*BLOCKY+BLOCKY/2
        if(placement == TOP):
            yoffset += 3*BLOCKY/8
        elif(placement == BOT):
            yoffset -= 3*BLOCKY/8

        imagebox = ob.OffsetImage(icon, zoom=0.25)
        ab = ob.AnnotationBbox(imagebox, (xoffset, yoffset), frameon=False)

        ax.add_artist(ab)