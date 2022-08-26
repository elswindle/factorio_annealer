# Factorio Annealer
  The Factorio annealer is a program that generates a cost optimized layout of blocks for a factory given a set of items to be produced.  Cost optimization is performed using a common place-and-route technique called simulated annealing.  Simply put, a random move is generated and is conditionally accepted based on a given cost function.  After a large number of moves, the design is considered optimized.  A blueprint is then generated by this layout that can be directly ported into Factorio.  Sets of sub items can be partitioned and all ingredients will be dedicated to make those items.  

## Background
  This idea has been floating around in my head for some years now, but I hadn't found a good use case for it until recently.  The main issue with this design initially was using large city blocks basically trivialized product generation.  Meaning a single block could potentially generate all the needed product for a very large (i.e. 1k science/min) base.  This made the problem of annealing a small number of large blocks not very interesting and could probably be done manually.  It wasn't until a few months ago, I saw a post on the Factorio subreddit about a city block implementation that was smaller than the typical chunk aligned one.  This got me thinking about how small could I make the city blocks and if simulated annealing could be applied here.  This was what finally got me to start this journey of creating 57 block blueprints and writing this annealer.  Additionally, shortly after starting writing the program, redruin1 posted an Alt-F4 post about his project to programmatically generate blueprints called Factorio Draftsman.  This was very fortuitous because it would save me the trouble of writing a program that imported a blueprint book, stitched hundreds (>200k total entities) of them together and then converted it back to a blueprint string to be imported into Factorio.  

# Top Level Organization
  At the top level, this program is comprised of 5 parts: factory, annealer, blueprinter, micro-block blueprints, and factory drawer.  The `Factory` class contains all item and recipe requirements and keeps track of the placement of the individual blocks.  The `Annealer` class takes the factory layout and performs the simulated annealing algorithm, including move generation, move evaluation and cost tracking.  The `Blueprinter` utilizes Factorio Draftsman and directs the creation of the blueprints of the factory.  The micro city blocks is a collection of blueprints that implement the required recipes for science pack production and research.  Finally, the `FactoryDrawer` class is a debug tool to visualize the current layout of the factory.  

## Factory
  The `Factory` class stores all related data concerning item requirements and physical placement. The factory placement is done using `FactoryBlocks` which consist of `FactoryCells`.  The `FactoryBlock` describes the physical implementation of a recipe which contains one or more `FactoryCell` objects.  The `FactoryCell` contains `FactoryCellIO` objects that specifies which item or fluid, whether it is an input or an output and which train station it is assigned to.  The factory also has pins which are raw resource interfaces with an external train/belt system.  Each solid item pin assumes 2 blue belts of the input come in at a time and each fluid pin assumes 25000/min.  
  
  The factory generates an item list and recipe list from vanilla game data by parsing the corresponding Lua files from the official `factorio-data` repository.  This is not a robust method, but learning to load all game data into Lua first and then extracting recipes and items from there was not something I wanted to do.  If this were to be implemented, this program could be extended to include mods and their items and recipes.  An important point to note here is that for items that have multiple recipes, each item can specify which is the preferred recipe.  In vanilla Factorio, this isn't a huge deal, but mods tend to have many different recipes that can generate the same item (i.e. wood, oxygen, rocket fuel in Krastorio 2).  In addition to vanilla items and recipes, some custom items and recipes are added to allow for ease of use in dealing with edge cases (top and bottom of recipe tree).  For example, a special `labs` recipe is created to handle the research and takes in all of the science packs as inputs with no outputs.  
  
  Each relevant recipe was implemented in game and stored as a `FactoryBlockTemplate`.  The templates specify required ingredients, products produced and at what rate along with some physical information regarding the placement of the train stations.  Some templates skip certain intermediate ingredients to avoid transporting too high of a volume of product.  THe most notable example is copper wire.  For electronic circuit production, far too much copper wire would need to be delivered and many blocks struggle with offloading the ingredients (i.e. armor-piercing ammo, electronic circuit, etc.).  
  
  Item requirement structures are implemented using a `Partition` class.  Partitions are a way to decouple cell dependencies in one tree from another.  Using default factory options, the only partition implemented is the `labs` recipe.  With a single partition, nothing special is implemented.  When additional partitions are added, the item requirement calculations are performed on a per partition basis.  The program can also be configured to implement separate LTN networks per partition.  This will restrict the available cells that can supply another.  For example, if we have a factory that has a electronic circuits and armor piercing ammo partitions, the amount of iron and copper plates are calculated separately.  The iron and copper plate blocks for electronic circuits will only supply electronic circuits and not armor piercing ammo and vice versa.  
  
  The program implements a simple, non-matrix based, calculator to generate the item requirements given the desired item production.  This works well for all items that only have a single recipe used.  In vanilla Factorio, this breaks down for oil products.  Petroleum gas can be generated via oil processing and light oil cracking.  How much to allocate to each of these recipes must be handled differently.  To handle these recipes, the calculator takes a bottom down approach.  First, the amount of refineries for heavy oil is calculated.  Second, light oil is calculated by first subtracting out excess light oil from heavy oil generation and then calculating the number of refineries are needed to cover the remaining light oil with all extra heavy oil is cracked into light oil.  Finally, petroluem gas production is calculated the same way as light oil.  The astute observer can tell this is not a very robust method to solve this problem.  If ever the amount of heavy oil or light oil is high enough that the excess petroleum gas is greater than is needed, an excess will accumulate.  This would result in an eventual dead lock caused by petroleum gas completely filling up.  A matrix based solver would be able prevent this kind of thing, but alas, I'm too lazy to implement it.  
  
## Micro City Blocks
  The factory blueprint is enabled by a library of custom cells I've coined as Micro City Blocks (MCB).  These are minimum sized train-based blocks that will allow 2 1-1 train stations (1 on top, 1 on bottom).  All in all, each cell is 36x32 tiles in size.  Each `FactoryBlockTemplate` has an associated blueprint within this library.  Due to the small size of each block and the desire to pack these as close together as possible, intersections were implemented without left turns.  Therefore, in order to turn left, a train must go straight and make 3 rights.  While this may be a bit longer distance wise, having left turns within the intersection would make it so any train entering the intersection block all other trains trying to enter the same intersection.  Meaning, a train going straight would block a train going the opposite direction.  This issue outweighed the need for left turns.  The train scheduling is done using the Logistic Train Network (LTN) mod to minimize the number of trains running at any given moment.  There are a total of 57 defined blocks, one for each recipe within the research recipe tree and a few auxiliary blueprints for LTN and resource interfaces at the edge of the factory.  This set can be extended to implement any item's recipe tree, but the current blueprint book contains on those related to the vanilla science packs.  
  
## Annealer
  The simulated annealing algorithm is implemented with in the `Annealer` class.  The main algorithm loop is quite simple: generate, evaluate and implement a move.  A move is simply selecting 2 factory blocks to swap.  Move generation is random but is constrained by blocks that contain more than 1 cell and by the number of adjacent LTN depots.  Factory blocks with more than 1 cell require the move generation to check for boundary cases in the other set of factory blocks being swapped (at edge).  Within the factory options, the user can specify the minimum number of LTN depots each cell must be adjacent to.  This means that for a value of 2, every cell must have 2 LTN depots adjacent.  Valid options are 0-6.  Edges require half the adjacent LTN depots and corners require none.  Once a valid move is generated, the algorithm evalutes the change in the cost function of the factory.  If the change results in a lower cost, the move is accepted.  If it incurs a higher cost, it is randomly accepted based on the change difference and temperature of the algorithm.  Simulated annealing starts with a high temperature.  This means that for early moves, a lot of higher cost moves will be accepted.  As the algorithm progresses, temperature falls and the probability that a bad move is accepted exponentially declinces.  The cost function consists of a simple distance value between origin and destination that the train would have to traverse and a function of the volume of trains is expected based on the producer->requester relationship (i.e. electronic circuits to processing units is high, iron gear wheels to satelite (radar) is low).  This volume is divided down by the amount of stations that are identical to the one in question.  For example, electronic circuits to processing units has a high volume, but if there are 100 processing unit blocks, the volume of trains to any individual block is divided by 100.  If a move is accepted, the factory implements this by swapping the sets of blocks.  This loop will continue until either a maximum number of iterations has occured or the average change of the past 32 moves is below some given function tolerance.

## Blueprinter
  As mentioned in the introduction, the ability to export the design into a valid Factorio blueprint was made possible using Factorio Draftsman and the imported MCB blueprint book.  Factorio Draftsman is an extremely powerful tool.  It allows the user to create a blueprint and add entities or modify existing entities within a programming environment.  If you visit the Alt-F4 page about it, you'll see a number of examples of what can be done with this tool including creating map images, ROM for a computer, preloaded turrets, etc.  If you've ever had a Factorio related idea that needs a blueprint created, Factorio Draftsman will fulfill all your needs. 
  
  After my shameless plug for Factorio Draftsman, back to the program at hand.  After importing the MCB blueprint book, each one is placed inside of a custom `factorio-draftsman` `Group` object.  Doing so allows the entities within a single blueprint to be handled all at once with minimal overhead.  When adding a `Group` to a `Blueprint`, draftsman makes a `deepcopy` of the `Group`, including each entity and any circuit connections and filters.  When adding the same block multiple times, this lets you simply set the position of one block, add it to the blueprint and then set the position for the next block without having worry about the first block's position being modified.  
  
  `Blueprinter` generates 2 blueprints for the factory.  The first blueprint consists of all factory cells.  Second is the connecting rail network and top level electric grid.  This is done mainly because the algorithm to connect power lines together is very slow in Draftsman.  In addition, a power pole can only accept 5 connections but because of the layout of the grid means many big electric poles will have 6 possible connections.  Using separate blueprints forces the game to take care of power poll connections.  

## Factory Drawer
  The `FactoryDrawer` allows the user to visualize the factory layout.  It generates a grid and places the item icon into the space it is placed.  Below is an example of this in action.  This is a powerful tool in debugging factory cell placement, cell dependencies and annealing.  It also allows the user to visualize a proposed move generated by the annealing process and contributing cells that affect the cost of the move.  

# Program Options
  The program provides options for the `Factory` and `Annealer` classes which will modify the behavior of the program and precision of the result.  

## Factory Options
  Here are the available options that can be modified.
  
  "top-items" : Top level item names and production rates for the factory to produce.  These cannot be a dependency of each other or of any of the top level items of the partitions.  Assignment and addition will check ensure this criteria is met. 
  
  "depot-adjacency-requirement" : Factory layout requirement for the number of LTN depots adjacent to each FactoryCell.  Default is 2, maximum is 6.
  
  "productivity-bonus" : Productivity bonus from a single module.  Vanilla bonuses are in [0, 0.04, 0.06, 0.1], default is prod-3 (0.1) 
  
  "calc-exceptions" : List of solids/fluids to be handled differently when calculating the factory requirements.  These will generally be items that can be produced via multiple recipes.  For vanilla Factorio, this includes oil products, i.e. light oil and petroleum.  Default items are heavy oil, light oil and petroluem gas.  If this is modified, the user must modify the `factorycalculator.calculateNormalizedRequirements` function to handle these items.  Additionally, the prerequisites to these items are not calculated.  Currently no functionality supports dealing with prerequisites of calculation exceptions (vanilla only has crude oil which is a resource and has no prerequisite itself).  
  
  "partitions" : List of all item names as top level partitions.  A partition is defined as a set of factory blocks that produce the resources needed to create the top item.  The size and requirements for these partitions are calculated based on the desired rate of the factory's top level items defined in "top-items".
  
  "partitioned-pins" : ** NOT YET IMPLEMENTED ** Specifies whether the pins will be global or partition specific.  If "use-unique-network" is set, the pins will be limited to supplying the partition only.  Otherwise, the pins will be laid out per partition instead of all together globally.  Not recommended without unique networks.
  
  "block-template-path" : Custom list of all block templates to be used in the factory.  For any partition, all sub-recipes must be defined within the given file.  If any block skips an intermediate product (i.e. electronic circuits request copper plates and makes copper wire onsite), that intermediate product MUST be skipped for ALL other recipes.  The block templates do not specify if they skip products at the moment.  During the calculation of factory requirements, the vanilla recipes are modified based on the provided block templates.  Having a block for an intermediate product that is skipped will break this functionality.  
  
  "use-unique-network" : Boolean specifying if the LTN train stations should operate using unique network ids.  This means blocks within a partition will only service blocks within the partition unless the item is the top item in a partition.  For example, if advanced circuits have their own partition, those factory blocks will have to be assigned to the advanced circuit partition blocks to get the needed resources and also assigned to any other partition network that uses them, i.e. chemical science packs.
  
  "aspect-ratio" : The x:y ratio of the factory.  This will try to size the factory to have aspect-ratio times more/less columns than rows. A value of 2 will cause it to be short and wide, while a value of 1/2 will make it tall and skinnier.

## Annealer Options
  Here are the available annealer options:
  
  "initial_temperature" : Specifies the initial randomness of the annealing algorithm.  The acceptance probability when a move increases the total cost function of the factory is calculates as exp(-cost_change/temperature).  For large temperatures, the probability is near 1 and will almost always accept bad moves.  The temperature decreases exponentially by the function initial_temperature/iteration.  Therefore, as the algorithm progresses, the probability to accept bad moves decreases and will eventually only accept moves that reduce the cost function.  Default is 1000
  
  "moves_per_iteration_ratio" : This helps calculate the number of moves to perform per iteration of the algorithm based on the number of factory cells in a given factory.  The iteration will only increment after the number of moves reaches the threshold calculated from factory_cells*moves_per_iteration_ratio.  So for a value of 0.1, a factory of 100 cells will perform 10 moves before incrementing the iteration and reducing the temperature of the algorithm.  A smaller value will result in more moves at higher temperatures.  Default is 0.1.
  
  "max_iterations" : Gives the algorithm a hard stopping point of iterations if the function tolerance cannot be met.  Default is 10000.
  
  "function_tolerance" : Defines the accuracy of the annealing algorithm.  If the average of the previous 32 moves is less than the function tolerance, the algorithm will end.  Higher values will result in a less optimal solution while smaller values will result in longer runtime and should produce a more optimal solution.  Default is 0.5.

# Installation
  I'm not very experienced with regards to setting up code that can be taken and ran by others, so this installation guide will not be optimal in the slightest.  

  1. Download this repository
  2. Install prerequisite data and programs.
      1. In the Factorio Annealer folder, clone into the official Factorio data repository
      2. Clone into the Factorio Drafstman repository
      3. From the Factorio Draftsman folder, run `python setup.py install`
      4. Download the following mods
          1. Logistics Train Network
          2. Inventory Sensor
      5. Copy the mods from the Factorio install location into the install location of Factorio Draftsman under `./draftsman/factorio-mods`.  This should be located with the other installed Python modules: `C:/Users/{user_name}/AppData/Local/Programs/Python/{Python version}/Lib/site-packages/factorio-draftsman-{version}-py{python_version}.egg/draftsman/factorio-mods`
      6. From the install location (see 2.v), run the draftsman update script
      7. Install the following Python modules
          1. lupa
          2. matplotlib
          3. pillow
          4. numpy
  3. Open `run_game.py` and modify the factory and annealer options
  4. Run `python run_game.py` 

  That should do it, but I'm sure it won't work like it did for me, so just open an issue and I'll fix it.  
