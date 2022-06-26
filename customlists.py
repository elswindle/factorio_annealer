from utils import *

if TYPE_CHECKING:
    from factory import Factory
    from item import Item
    from partition import Partition

class PartitionDict(dict):
    def __init__(self, parent, top_items):
        # type: (Factory, list[Item], **dict) -> None
        super(PartitionDict, self).__init__()
        self.factory = parent

        for item in top_items:
            self[item] = Partition(item)

    def __setitem__(self, item, partition) -> None:
        self.factory.testTopDependency(item)
        return super(PartitionDict, self).__setitem__(item, partition)

class FactoryTopItemList(list):
    def __init__(self, parent, top_items):
        # type: (Factory, list[Item]) -> None
        super(FactoryTopItemList, self).__init__()
        self.factory = parent

        for item in top_items:
            self.append(item)

    def append(self, item):
        # type: (Item) -> None
        self.factory.testTopDependency(item)
        for top in self.factory.top_items:
            self.factory.testDependenceToTop(item)

        return super().append(item)