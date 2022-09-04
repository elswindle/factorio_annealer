from constants import PIN_CORNER_PADDING


class FactoryOptions:
    def __init__(
        self,
        top=[["labs", 1000]],
        aspect_ratio=1,
        dar=2,
        prod_level=3,
        exceptions=["heavy-oil", "light-oil", "petroleum-gas"],
        block_template_path="data/factory_block_templates.csv",
        use_unique_network=True,
        partitions=[],
        partition_pins=False,
        pin_padding=PIN_CORNER_PADDING,
    ):
        if prod_level == 0:
            prod_bonus = 0
        elif prod_level == 1:
            prod_bonus = 0.04
        elif prod_level == 2:
            prod_bonus = 0.06
        else:
            prod_bonus = 0.1

        self.factory_args = {}
        self.factory_args["top-items"] = top
        self.factory_args["depot-adjacency-requirement"] = dar
        self.factory_args["productivity-bonus"] = prod_bonus
        self.factory_args["calc-exceptions"] = exceptions
        self.factory_args["block-template-path"] = block_template_path
        self.factory_args["use-unique-network"] = use_unique_network
        self.factory_args["partitions"] = partitions
        self.factory_args["aspect-ratio"] = aspect_ratio
        self.factory_args["partition-pins"] = partition_pins
        self.factory_args["pin-padding"] = pin_padding

    def addFactoryArg(self, name, value):
        self.factory_args[name] = value

    def getFactoryArgs(self):
        return self.factory_args
