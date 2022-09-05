# Factory and Annealer Options
  This section will cover some of the effects of different factory and annealer options described in the main README.  

## Before and after with default settings
<p align="middle">
  <img src="./base_b4.png" width="45%" />
  <img src="./base_after.png" width="45%" /> 
</p>

## Different top level items 
  New top level items are 50k plastic bar/min and 2.5k military science/min
<p align="middle">
  <img src="./pb_50k_ms_2.5k.png" width="45%" />
  <img src="./pb_50k_ms_2.5k_after.png" width="45%" /> 
</p>

## Lower productivity bonus
  Compare productivity module 3s (left) to productivity module 1s (right)
<p align="middle">
  <img src="./base_b4.png" width="45%" />
  <img src="./prod1.png" width="45%" /> 
</p>

## Added partitions
  Compare initial layout of base settings (left) and 3 added partitions: logistic science pack, utility science pack and processing units (right).  Notice it is slightly larger since there is some granularity to the cells.  For example, the logistic science pack partition requires a electronic circuit cell, but doesn't need the full output of the cell (~1 BB).  This can also be seen in the number of coal pins.  
<p align="middle">
  <img src="./base_b4.png" width="45%" />
  <img src="./part_log_utility_BC.png" width="45%" /> 
</p>

## Partitioned pins
  Compare the optimized layout of the partitioning above (left) and post optimization with partitioned pins (right).  Notice that the partitions are not well defined with global pins.  The factory cells of the individual partitions are lost in the sea of other cells.  The partitions can be seen quite well in the partitioned pins version.
<p align="middle">
  <img src="./part_log_utility_BC_after.png" width="45%" />
  <img src="./part_pin.png" width="45%" /> 
</p>

## Aspect ratio of 3
![asdf1](./aspect3.png?raw=true)

## Different pin padding
![asdf2](./pad4.png)

## Function tolerance change
  Compare the base settings optimized layout (ftol=0.5, left) and the layout of with a function tolerance of 5 (right).  Notice how much more optimized the layout with lower tolerance.  
<p align="middle">
  <img src="./base_after.png" width="45%" />
  <img src="./ftol5.png" width="45%" /> 
</p>

## Multiple settings example
  The following layout modifies multiple settings, including partitioned pins, pin padding and all sciences have separate partitions.
![asdf1](./full_part.png?raw=true)
