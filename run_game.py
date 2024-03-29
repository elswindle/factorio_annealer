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
    bpter = Blueprinter("data/micro_blocks_v1.0.txt")

    parts = [
        "automation-science-pack",
        "logistic-science-pack",
        "military-science-pack",
        "chemical-science-pack",
        "production-science-pack",
        "utility-science-pack",
        "space-science-pack",
    ]
    top = [["labs", 250]]
    fopts = FactoryOptions(
        top=top, partitions=parts, partition_pins=True, pin_padding=3
    )
    aopts = AnnealerOptions(function_tolerance=0.2)

    base_factory = Factory(**fopts.factory_args)
    base_factory.buildFactory()
    fd = FactoryDrawer(base_factory)

    fd.drawFactory()
    plt.show()

    factory_annealer = Annealer(base_factory, **aopts.annealer_args)
    factory_annealer.anneal()

    bpter.generateFactoryBlueprint(base_factory)
    fd.drawFactory()
    plt.show()


if __name__ == "__main__":
    main()
