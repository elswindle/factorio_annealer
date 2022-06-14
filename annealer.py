from factoryblock import FactoryBlock
from factorycell import FactoryCell
from factorycellio import FactoryCellIO
from factory import Factory
from factorydrawer import FactoryDrawer
from partition import Partition
from routegroup import RouteGroup
from globals import *
import random
from math import ceil

def blockLength(block):
    if(block == -1):
        return 1
    elif(isinstance(block, FactoryBlock)):
        return len(block.fcells)
    else:
        print("not a factory block")
        return -1

class Annealer:
    def __init__(self, factory):
        # type: (Factory) -> None
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
                    new_rg = RouteGroup(producer, requester, tpm)
                    
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

    def getPartitionCost(self, partition):
        # type: (Partition) -> None
        cost = 0
        for rg in self.route_groups[partition]:
            cost += len(rg)
        return cost

    def generateMove(self, inloc1=-1, inloc2=-1):
        # type: (Location, Location) -> None
        f = self.factory.factory

        move_generated = False
        while(not move_generated):
            cell_group1 = []
            cell_group2 = []
            if(inloc1 == -1 or inloc2 == -1):
                loc1, loc2 = self.generateMoveCoordinates()
            else:
                loc1 = inloc1
                loc2 = inloc2
            cell1 = f[loc1.x][loc1.y]
            cell2 = f[loc2.x][loc2.y]
            if(cell1 == EMPTY or cell2 == EMPTY):
                continue

            block1 = cell1.parent_block
            block2 = cell2.parent_block

            # Both size 1
            if(blockLength(block1) == 1 and blockLength(block2) == 1):
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
                        # Throw away move if the next cell is more than 1 cell
                        if(blockLength(cell2.parent_block) > 1):
                            all_valid = False
                            break
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
                        # Throw away move if the next cell is more than 1 cell
                        if(blockLength(cell1.parent_block) > 1):
                            all_valid = False
                            break
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
                        
                        for i in range(block1.dimension.x):
                            abs_loc1 = block1.location + rel_loc1
                            abs_loc2 = block2.location + rel_loc2
                            abs_loc1.x += i
                            abs_loc2.x += i

                            cell_group1.append(f[abs_loc1.x][abs_loc1.y])
                            cell_group2.append(f[abs_loc2.x][abs_loc2.y])

                        move_generated = True
                    elif(block1.dimension.y > block1.dimension.x):
                        rel_loc1.y += -block1.num_below
                        rel_loc2.y += -block2.num_below

                        for i in range(block1.dimension.y):
                            abs_loc1 = block1.location + rel_loc1
                            abs_loc2 = block2.location + rel_loc2
                            abs_loc1.y += i
                            abs_loc2.y += i

                            cell_group1.append(f[abs_loc1.x][abs_loc1.y])
                            cell_group2.append(f[abs_loc2.x][abs_loc2.y])

                        move_generated = True

            self.setTestLocations(cell_group1, cell_group2)
            # Check depot and duplication requirements
            if(move_generated):
                cell : factorycell.FactoryCell
                for cell in (cell_group1 + cell_group2):
                    # Don't need to check depots in their new location
                    if(not cell.is_depot):
                        center = cell.tl
                        xmax = self.factory.dimensions.x
                        ymax = self.factory.dimensions.y
                        for xofst in range(-1,2):
                            for yofst in range(-1,2):
                                x = center.x + xofst
                                y = center.y + yofst

                                if(x < 1 or x > xmax or y < 1 or y > ymax):
                                    curr_cell = EMPTY
                                else:
                                    curr_cell = self.factory.tf[x][y]
                                    if(not curr_cell.is_depot):
                                        depot_req = DEPOT_REQ

                                        # Ignore depot requirement for corners
                                        if((x == 1 or x == xmax) and (y == 1 or y == ymax)):
                                            depot_req = 0
                                        # If edge, reduce by half, rounded up
                                        if(x == 1 or x == xmax or y == 1 or y == ymax):
                                            depot_req /= 2
                                            depot_req = ceil(depot_req)

                                        num_depots = self.numAdjacentDepots(self.factory.tf[x][y])
                                        if(num_depots < depot_req):
                                            move_generated = False

                # Throw out a move if the groups overlap
                for c1 in cell_group1:
                    for c2 in cell_group2:
                        if(c1 == c2):
                            move_generated = False

                # Throw out a move if the groups swap identical items from same partition
                # TODO

            if(inloc1 != -1 and inloc2 != -1):
                move_generated = True

            if(not move_generated):
                self.resetTestLocations(cell_group1, cell_group2, False)

        return cell_group1, cell_group2

    def numAdjacentDepots(self, cell):
        # type: (FactoryCell) -> None
        if(cell == EMPTY):
            return 9
        if(cell.recipe.item.is_resource):
            return 9
        tf = self.factory.tf
        num = 0
        base_loc = cell.location
        for xofst in range(-1,2):
            for yofst in range(-1,2):
                if(xofst == 0 and yofst == 0):
                    continue
                x = base_loc.x + xofst
                y = base_loc.y + yofst
                cell = tf[x][y]

                if(cell != EMPTY):
                    if(cell.is_depot):
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

    def evaluateMove(self, cg1, cg2, fd=-1):
        # type: (list[FactoryCell], list[FactoryCell], FactoryDrawer) -> None
        cost_change = []
        
        for cell in cg1 + cg2:
            cost_change.append(0)
            if(not cell.is_depot):
                ip_change = 0
                # Iterate on requesters within the cell
                for requester in cell.inputs:
                    req_loc = requester.location
                    req_tl = requester.tl
                    req_pm = requester.placement

                    rg_change = 0
                    # Iterate on route groups of requester
                    for rg in requester.route_groups:
                        if(fd != -1):
                            fd.drawRoutes(rg.producers, [requester])
                        # Iterate on producers of the requested item
                        for producer in rg.producers:
                            prod_loc = producer.location
                            prod_pm = producer.placement
                            # Check to see if the producer is also being swapped
                            if(producer.tl == -1):
                                prod_tl = prod_loc
                            else:
                                prod_tl = producer.tl
                            # Get the current cost of the route
                            curr_cost = calculateDistanceCost(prod_loc, req_loc, prod_pm, req_pm)
                            test_cost = calculateDistanceCost(prod_tl, req_tl, prod_pm, req_pm)

                            rg_change += test_cost - curr_cost

                    ip_change += (rg_change * rg.trains_per_min / len(rg.requesters))

                op_change = 0
                for producer in cell.outputs:
                    prod_loc = producer.location
                    prod_tl = producer.tl
                    prod_pm = producer.placement

                    rg_change = 0
                    for rg in producer.route_groups:
                        if(fd != -1):
                            fd.drawRoutes([producer], rg.requesters)
                        for requester in rg.requesters:
                            req_loc = requester.location
                            req_pm = requester.placement
                            # Check to see if the requester is also being swapped
                            if(requester.tl == -1):
                                req_tl = req_loc
                            else:
                                req_tl = requester.tl
                            # Get the current cost of the route
                            curr_cost = calculateDistanceCost(prod_loc, req_loc, prod_pm, req_pm)
                            test_cost = calculateDistanceCost(prod_tl, req_tl, prod_pm, req_pm)
                    
                        rg_change += test_cost - curr_cost

                    op_change += (rg_change * rg.trains_per_min / len(rg.producers))

                cost_change[len(cost_change)-1] += ip_change + op_change

        total_change = 0
        for cc in cost_change:
            total_change += cc
        # print(cost_change)
        # If the cost is negative, accept move
        # Negative values means curr_cost > test_cost
        if(total_change <= 0):
            return True
        else:
            self.resetTestLocations(cg1, cg2, False)
            return False
            # Randomly choose to accept move if cost_change is > 0
            # This chance will be higher with higher temperature
            # print("temperature")

    def setTestLocations(self, cg1, cg2):
        # type: (list[FactoryCell], list[FactoryCell]) -> None
        for idx in range(len(cg1)):
            # Update block location only once
            new_loc1 = cg2[idx].location - cg1[idx].offset
            new_loc2 = cg1[idx].location - cg2[idx].offset

            if(not cg1[idx].is_depot):
                cg1[idx].parent_block.tl = new_loc1
            if(not cg2[idx].is_depot):
                cg2[idx].parent_block.tl = new_loc2

            cg1[idx].setTestLocation(new_loc1)
            cg2[idx].setTestLocation(new_loc2)

            x = cg1[idx].tl.x
            y = cg1[idx].tl.y
            self.factory.tf[x][y] = cg1[idx]
            x = cg2[idx].tl.x
            y = cg2[idx].tl.y
            self.factory.tf[x][y] = cg2[idx]

    def resetTestLocations(self, cg1, cg2, accepted):
        # type: (list[FactoryCell], list[FactoryCell], bool) -> None
        for idx in range(len(cg1)):
            # Only swap back the test factory if the move was not accepted
            if(not accepted):
                x = cg1[idx].location.x
                y = cg1[idx].location.y
                self.factory.tf[x][y] = cg1[idx]
                x = cg2[idx].location.x
                y = cg2[idx].location.y
                self.factory.tf[x][y] = cg2[idx]

            cg1[idx].resetTestLocation()
            cg2[idx].resetTestLocation()

    def performMove(self, cg1, cg2):
        # type: (list[FactoryCell], list[FactoryCell]) -> None
        # Reset the test locations of the blocks but not the test factory
        self.resetTestLocations(cg1, cg2, True)
        
        for idx in range(len(cg1)):
            # Update block location only once
            new_loc1 = cg2[idx].location - cg1[idx].offset
            new_loc2 = cg1[idx].location - cg2[idx].offset

            if(not cg1[idx].is_depot):
                cg1[idx].parent_block.location = new_loc1
            if(not cg2[idx].is_depot):
                cg2[idx].parent_block.location = new_loc2

            cg1[idx].setLocation(new_loc1)
            cg2[idx].setLocation(new_loc2)
            # temp_loc = cg1[idx].location
            # cg1[idx].location = cg2[idx].location
            # cg2[idx].location = temp_loc
            
            x = cg1[idx].location.x
            y = cg1[idx].location.y
            self.factory.factory[x][y] = cg1[idx]
            x = cg2[idx].location.x
            y = cg2[idx].location.y
            self.factory.factory[x][y] = cg2[idx]