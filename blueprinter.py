import factory
# from draftsman import Blueprint, BlueprintBook
import draftsman.classes.blueprint
import draftsman.blueprintable

class Blueprinter:
    def readBlueprint(self, path):
        file = open(path)
        # bp_str = file.readline()
        # bp_str.rstrip('\n')
        bp_str = "0eJytldtugzAMht/F10kFAUrhcq8xVRMHq4sGgZFQrap495m2q6i2laT0ikPs/4ud/MkR8qrHtpPKQHoEWTRKQ/p6BC13KqvGf+bQIqQgDdbAQGX1+JVjRqEwMJCqxC9I/YHNJlVZPskQw5YBKiONxDNzEsagbTSNEIPUKJr7q4jBgdJWEWmUssPiPOxdVA5vqq9z7Ggu7ATWY2rbNWVPkXsK4DW9V8iDET7O97aY38zgwozmmWLC1C1i6Qzz7GHBUpiwZ4W2LG2y4oNLpbEzlPh/gd48NHLQdZBdT2SrZie1kQUv3lEb3uFnT8+7E+cWiPghhAth80jPR/vcCoe/hJMHmm6j63vTnvxl7h9vj4abNffT3H2tYW1BXexv4UJbbHAuHHaUb+3xu6tnczJHT1o8p/LWi8rjTrszfvbdY7VfNvcr3J6HR9z1tmewx06fBMXGD+NExKFIkiAhf1EfkK5xeLlGD8M3Wc6mIQ=="
        print(bp_str)
        bp = draftsman.blueprintable.get_blueprintable_from_string(bp_str)

        print(bp)

    def generateFactoryBlueprint(self, factory):
        print("hello")