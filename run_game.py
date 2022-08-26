from annealer import Annealer
from factorydrawer import FactoryDrawer
from game import Game
from factory import Factory
from partition import Partition
from utils import *
import matplotlib.pyplot as plt
from blueprinter import Blueprinter
from factoryoptions import FactoryOptions
from annealeroptions import AnnealerOptions


def main():
    # bpter = Blueprinter("data/micro_blocks_v1.0.txt")

    parts = [
        "logistic-science-pack", 
        "space-science-pack", 
        "automation-science-pack", 
        "chemical-science-pack", 
        "production-science-pack", 
        "utility-science-pack", 
        "military-science-pack"
    ]
    fopts = FactoryOptions(dar=2, top=[["labs", 100]], partitions=parts, aspect_ratio=1.8)
    aopts = AnnealerOptions(function_tolerance=0.01,max_iterations=10000)

    base_factory = Factory(**fopts.factory_args)
    base_factory.buildFactory()

    factory_annealer = Annealer(base_factory, **aopts.annealer_args)
    factory_annealer.anneal()

    fd = FactoryDrawer(base_factory)
 
    # bpter.generateFactoryBlueprint(base_factory)
    fd.drawFactory()
    plt.show()

    print("done")

if __name__ == "__main__":
    main()
