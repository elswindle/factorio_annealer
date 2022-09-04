from utils import *
from partition import Partition

if TYPE_CHECKING:
    from factory import Factory
    from item import Item


class PartitionDict(dict):
    def __init__(self, parent, top_items):
        # type: (Factory, list[Item]) -> None
        super(PartitionDict, self).__init__()
        self.factory = parent  # type: Factory

        id = len(parent.partitions)
        for id, item in enumerate(top_items):
            self[item] = Partition(item, id)

    def __setitem__(self, item, partition):
        # type: (Item, Partition) -> None
        if partition.main:
            self.testDependenceToTop(item, item)
        else:
            self.testTopDependency(item)
        return super(PartitionDict, self).__setitem__(item, partition)

    def testTopDependency(self, item):
        # type: (Item) -> bool
        """
        Check to see if one of the factory's top level items is a dependency of
        the given partition item.  If it is violated, the factory will double up on
        the top item's dependencies.  This function checks each input of the
        item's recipe and then recursively checks their recipes.

        :param item: Item to test if inside factory's top items

        :exception AttributeError: if ``item`` is part of factory's top items

        :returns: True if completed
        """
        for part in self.values():
            if part.main and item == part.top_item:
                raise AttributeError(
                    "Factory top items must not be a dependency of another top item\n"
                    + "Offending item: "
                    + str(item)
                )
        recipe = item.preferred_recipe
        for ingredient_name in recipe.ingredients:
            ingredient = self.factory.item_list[ingredient_name]

            # Test ingredient's recipe
            if not ingredient.is_resource:
                self.testTopDependency(ingredient)

        return True

    def testDependenceToTop(self, item, curr_item):
        # type: (Item, Item) -> bool
        """
        This tests to make sure any new top level items are not a dependency of any other
        top level items.  Similar to testTopDependency, doing so would create circular
        item dependencies.  This will basically implement the former function, but
        start at the current top items and traverse their recipe tree looking for
        the given item

        :param item: Item to search for in top level recipe tree

        :param curr_item: Current item in the tree search

        :exception AttributeError: if ``item`` is a dependecy of a top item

        :returns: True if completed
        Fix this later
        """
        return True

        # iterate on main partitions
        # recursively traverse item tree
        # If curr_item==item, raise error
        for part in self.values():
            if not part.main:
                raise AttributeError(
                    "A new top Factory item must not be dependent on current top items\n"
                    + "Offending item: "
                    + str(item)
                )
        # If an item doesn't have a recipe, we're at the top of the tree, call it good
        try:
            recipe = item.preferred_recipe
        except:
            return True

        for product_name in recipe.products:
            product = self.factory.item_list[product_name]

            self.testDependenceToTop(product)

        return True


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
