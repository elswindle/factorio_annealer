class FactoryOptions:
    def __init__(
        self,
        top=[["labs", 1000]],
        dar=2,
        prod_level=3,
        exceptions=["heavy-oil", "light-oil", "petroleum-gas"],
        block_template_path="data/factory_block_templates.csv",
        use_unique_network=True,
        partitions=[],
    ):
        self.top_items = top
        self.depot_adjacency = dar
        self.productivity_level = prod_level
        self.calc_exceptions = exceptions
        self.block_template_path = block_template_path
        self.unique_network = use_unique_network
        self.partitions = partitions

        if self.productivity_level == 0:
            self.productivity_bonus = 0
        elif self.productivity_level == 1:
            self.productivity_bonus = 0.04
        elif self.productivity_level == 2:
            self.productivity_bonus = 0.06
        else:
            self.productivity_bonus = 0.1

        self.factory_args = {}
        self.factory_args["top-items"] = self.top_items
        self.factory_args["depot-adjacency-requirement"] = self.depot_adjacency
        self.factory_args["productivity-bonus"] = self.productivity_bonus
        self.factory_args["calc-exceptions"] = self.calc_exceptions
        self.factory_args["block-template-path"] = self.block_template_path
        self.factory_args["use-unique-network"] = self.unique_network
        self.factory_args["partitions"] = self.partitions

    def addFactoryArg(self, name, value):
        self.factory_args[name] = value

    def getFactoryArgs(self):
        return self.factory_args
