from shutil import move
import factoryblock
import factory
import partition
from globals import *
import routegroup
import random

def blockLength(block):
    if(block == -1):
        return 1
    elif(isinstance(block, factoryblock.FactoryBlock)):
        return len(block.fcells)
    else:
        print("not a factory block")
        return -1

class Annealer:
    def __init__(self, factory : factory.Factory):
        random.seed()
        self.factory = factory
        self.route_groups = {}              # Partition : Item : Recipe : RouteGroup
        self.temperature = INITIAL_TEMP

    def initializeRouteGroups(self):
        for part in self.factory.partitions.values():
            reqs_bd = part.reqs_breakdown
            if(self.route_groups.get(part) is None):
                self.route_groups[part] = {}

            # Iterate item requirements
            for producer in reqs_bd.keys():                 # producer is Item
                if(self.route_groups[part].get(producer) is None):
                    self.route_groups[part][producer] = {}
                # Iterate on recipe requesters
                for requester in reqs_bd[producer].keys():  # requester is Recipe
                    rate = reqs_bd[producer][requester]
                    stack_size = producer.stack_size
                    if(producer.is_fluid):
                        train_size = 25000
                    else:
                        train_size = stack_size * 40
                    tpm = rate / train_size                 # Trains have 40 inventory slots
                    new_rg = routegroup.RouteGroup(producer, requester, tpm)
                    
                    self.route_groups[part][producer][requester] = new_rg

    def populateRouteGroups(self):
        # for each partition, create delivery vectors
        # between each factorycellio producer and requester
        # and assign to the route group
        # 
        # Iterate through partitions
        for part in self.route_groups.keys():
            part.populateRouteGroups(self.factory, self.route_groups[part])

    def getFactoryCost(self):
        cost = 0
        for part in self.factory.partitions:
            cost += self.getPartitionCost(part)
        return cost

    def getPartitionCost(self, partition : partition.Partition):
        cost = 0
        for rg in self.route_groups[partition]:
            cost += len(rg)
        return cost

    def generateMove(self, inloc1=-1, inloc2=-1):
        cell_group1 = []
        cell_group2 = []
        f = self.factory.factory

        move_generated = False
        while(not move_generated):
            if(inloc1 == -1 or inloc2 == -1):
                loc1, loc2 = self.generateMoveCoordinates()
            else:
                loc1 = inloc1
                loc2 = inloc2
            cell1 = f[loc1.x][loc1.y]
            cell2 = f[loc2.x][loc2.y]
            block1 = cell1.parent_block
            block2 = cell2.parent_block

            # Both size 1
            if(blockLength(block1) == 1 or blockLength(block2) == 1):
                cell_group1.append(cell1)
                cell_group2.append(cell2)

                # If both depot, 
                if(cell1.is_depot and cell2.is_depot):
                    move_generated = False
                else:
                    move_generated = True
            # Cell1 > 1, cell2 = 1
            elif(blockLength(block1) > 1 and blockLength(block2) == 1):
                ofst = cell1.offset
                all_valid = True
                for cell in block1.fcells:
                    rel_ofst = cell.offset - ofst
                    abs_loc1 = loc1 + rel_ofst
                    abs_loc2 = loc2 + rel_ofst

                    if(validLocations([abs_loc1, abs_loc2], self.factory)):
                        cell1 = f[abs_loc1.x][abs_loc1.y]
                        cell2 = f[abs_loc2.x][abs_loc2.y]
                        cell_group1.append(cell1)
                        cell_group2.append(cell2)
                    else:
                        all_valid = False
                        break
                
                if(all_valid):
                    move_generated = True
            # Cell2 > 1, cell1 = 1
            elif(blockLength(block1) == 1 and blockLength(block2) > 1):
                ofst = cell2.offset
                all_valid = True
                for cell in block2.fcells:
                    rel_ofst = cell.offset - ofst
                    abs_loc1 = loc1 + rel_ofst
                    abs_loc2 = loc2 + rel_ofst

                    if(validLocations([abs_loc1, abs_loc2], self.factory)):
                        cell1 = f[abs_loc1.x][abs_loc1.y]
                        cell2 = f[abs_loc2.x][abs_loc2.y]
                        cell_group1.append(cell1)
                        cell_group2.append(cell2)
                    else:
                        all_valid = False
                        break
                
                if(all_valid):
                    move_generated = True
            # Both > 1
            elif(blockLength(block1) > 1 and blockLength(block2) > 1):
                # Dimensions match
                if(block1.dimension == block2.dimension):
                    rel_loc1 = Location(0,0)
                    rel_loc2 = Location(0,0)
                    if(block1.dimension.x > block1.dimension.y):
                        rel_loc1.x += -block1.num_left
                        rel_loc2.x += -block2.num_left
                        
                        for i in range(len(block1.dimension.x)):
                            abs_loc1 = block1.location + rel_loc1 + i
                            abs_loc2 = block2.location + rel_loc2 + i

                            cell_group1.append(f[abs_loc1.x][abs_loc1.y])
                            cell_group2.append(f[abs_loc2.x][abs_loc2.y])

                        move_generated = True
                    elif(block1.dimension.y > block1.dimension.x):
                        rel_loc1.y += -block1.num_below
                        rel_loc2.y += -block2.num_below

                        for i in range(len(block1.dimension.y)):
                            abs_loc1 = block1.location + rel_loc1 + i
                            abs_loc2 = block2.location + rel_loc2 + i

                            cell_group1.append(f[abs_loc1.x][abs_loc1.y])
                            cell_group2.append(f[abs_loc2.x][abs_loc2.y])

                        move_generated = True

            # Check depot and duplication requirements
            if(move_generated):
                for idx in range(len(cell_group1)):
                    if(cell_group1[idx].is_depot):
                        for xofst in range(-1,2):
                            for yofst in range(-1,2):
                                base_loc = cell_group1[idx].location
                                x = base_loc.x + xofst
                                y = base_loc.y = yofst

                                depot_req = DEPOT_REQ
                                # If corner, ignore requirement
                                if(x == 1 and (y == 1 or y == self.factory.dimensions.y)):
                                    depot_req = 0
                                elif(x == self.factory.dimensions.x and (y == 1 or y == self.factory.dimensions.y)):
                                    depot_req = 0
                                # If edge, reduce by 1
                                elif(x == 1 or x == self.factory.dimensions.x):
                                    depot_req -= 1
                                elif(y == 1 or y == self.factory.dimensions.y):
                                    depot_req -= 1

                                num_depots = self.numAdjacentDepots(f[x][y])
                                if(x != 0 or y != 0):
                                    num_depots -= 1
                                if(num_depots < depot_req):
                                    mov_generated = False

                    if(cell_group2[idx].is_depot):
                        for xofst in range(-1,2):
                            for yofst in range(-1,2):
                                base_loc = cell_group2[idx].location
                                x = base_loc.x + xofst
                                y = base_loc.y = yofst

                                depot_req = DEPOT_REQ
                                # If corner, ignore requirement
                                if(x == 1 and (y == 1 or y == self.factory.dimensions.y)):
                                    depot_req = 0
                                elif(x == self.factory.dimensions.x and (y == 1 or y == self.factory.dimensions.y)):
                                    depot_req = 0
                                # If edge, reduce by 1
                                elif(x == 1 or x == self.factory.dimensions.x):
                                    depot_req -= 1
                                elif(y == 1 or y == self.factory.dimensions.y):
                                    depot_req -= 1

                                num_depots = self.numAdjacentDepots(f[x][y])
                                if(x != 0 or y != 0):
                                    num_depots -= 1
                                if(num_depots < depot_req):
                                    mov_generated = False

                for c1 in cell_group1:
                    for c2 in cell_group2:
                        if(c1 == c2):
                            move_generated = False

            if(inloc1 != -1 and inloc2 != -1):
                move_generated = True

        return cell_group1, cell_group2

    def numAdjacentDepots(self, cell):
        if(cell == EMPTY):
            return 9
        f = self.factory.factory
        num = 0
        base_loc = cell.location
        for xofst in range(-1,2):
            for yofst in range(-1,2):
                if(xofst == 0 and yofst == 0):
                    continue
                x = base_loc.x + xofst
                y = base_loc.y + yofst

                if(f[x][y].is_depot):
                    num += 1

        return num

    def generateMoveCoordinates(self):
        x1 = random.randint(1, self.factory.dimensions.x)
        x2 = random.randint(1, self.factory.dimensions.x)
        y1 = random.randint(1, self.factory.dimensions.y)
        y2 = random.randint(1, self.factory.dimensions.y)

        loc1 = Location(x1,y1)
        loc2 = Location(x2,y2)

        return loc1, loc2