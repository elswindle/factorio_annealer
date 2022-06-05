import factory
# from draftsman import Blueprint, BlueprintBook
import draftsman.classes.blueprint
import draftsman.blueprintable

class Blueprinter:
    def readBlueprint(self, path):
        file = open(path)
        bp_str = file.readline()
        print(bp_str)
        bp = draftsman.blueprintable.get_blueprintable_from_string(bp_str)

        print(bp)        

    def generateFactoryBlueprint(self, factory):
        print("hello")