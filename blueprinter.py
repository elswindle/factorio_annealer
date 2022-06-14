import factory
from factory_blueprint import FactoryCellGroup
from globals import *
from draftsman.classes.blueprint import Blueprint
from draftsman.classes.blueprintbook import BlueprintBook
from draftsman.classes.group import Group
# from draftsman import utils
import sys

class Blueprinter:
    def __init__(self, bpb_path=EMPTY, factory=EMPTY):
        if(bpb_path is not EMPTY):
            bpb_file = open(bpb_path)
            self.bpb_str = bpb_file.readline()

            self.ub_book = BlueprintBook(self.bpb_str)
        else:
            self.ub_book = BlueprintBook()

        self.factory = factory
        self.fcgroups = {}          # recipe : FactoryCellGroup

    def loadBlueprintBookString(self, path):
        file = open(path)
        self.bpb_str = path.readline()

        self.ub_book.load_from_string(self.bpb_str)

    def generateFactoryCellGroups(self):
        pass
        
    def readBlueprint(self, path):
        pass

    def testFactoryCellGroup(self):
        pass

    def testEntityTransfer(self, path=""):
        # f = open(path)
        # bp_str = f.readline()
        bp_str = "0eNqdmt1u4jAQhd8l16Gyx7Ed8yqragU06kaiCQqh2qri3TcpPyplspyTS1ryceKZsY/H/szW20O16+qmz5afWb1pm322/PWZ7evXZrUd/9Z/7KpsmdV99ZblWbN6Gz91q3qbHfOsbl6qv9nSHp/zrGr6uq+r0/NfHz5+N4e3ddUNX7g+ue+HZ1//9IsvRJ7t2v3wVNuMPzWSUp59jMBjfgeRK2Rdvy6qbbXpu3qz2LXb6h4kcgYND1XDD67bQzdK8zEP7lmhO1Si+GmJBfmeToN4UokKCaQSr0EiqUSFlFfI5tC9Vy9TOsrTsJohYi91NwT3639eISby3aImyxpMlwRVV6EhLTleujAhXy+pFDafdQqb0FYtC8um9AQmgKl0rv1wGzLRkHCK27Mydwt1GrS8mSgXmz+rulmcp9R7cPF0RsuTv4VbDc5mv1XnBzFsSHQMnvJJHT+tvkWwODs9zlFDOiYkkiZDosVbilv4FLa8UP1Pqpaa4qksChw8UPB4gQ+5qqZBZJNSx1CFI8K9cmIzXtXoDKUxUhqdpeDhe1geLk9OGLjznHJ4vbEnagSY8OrjcCa8FHmcCZutiDPhiko4s4RjRAQJX4/wKBWGXZYRKL4LweNUsG7NqqavcDzmsTa4fgSPd4F7OSLegZ2bEWjkoRoGrhoh0iaxvgmAerhqHB5vD1eNw+Pt4apxeLw9XEMOD5TH1yAiUHANFUSg4BoqiEBFpulyEivmZ9NFcitWa7r4b4avXbe7tusVuReqBkjzfGzSfWww7DSsbpsD2wiYwAgyOuY/wxMcE75zXhDxC2x/QNSNfWD7AxOYMMs9i0Hcc4icwRX3uLpCyRlciJk4g4swo+EMLsS0VDNHisf78CicZ4ZkOtIzQ9CC9MwQ1JOeGYIG0jNDULZbIGrvKZY85rG2RHpmBFoa0jNDUHaRgaDCQzWMIz0zpK2g2oI/Z4ygIT1pwyGdgbThEDSSNhyClqQNh6CJtOEINBnShkNQS9pwCCqkDYegVPv60meWu7agVgOpYNeN+PiUIvlZvly87stTmNULBweAXo50jVzz2nIa2ea1rtEaw0548fHhijV2Vk8ce3VrZJ6t94itt8ZhhzfXfjiquqDOvZ3R4+VnHSWOQ4zEjb0lIBNH6ZE6S3cGOOY0JZvxE9rSrJO/+xH06ok/2zAQ/ZydvjowxWHb0U4/aaevD0xx6BsxTufQl2ImOGzGO30etWxveYrD7mGcnuWWXR8mOMLms9Pz8Nu9APyy1sBCb2tZYTcqo9Dn/HSPbfnt2luevVfd/uS8SlvEJNGHYUWzcjz+Az5/z8Y="
        # bp_str = "0eJy9WNtu4zYQ/RWCz5JhXe0YRX9gF9iHYosC3YUhS7RNRCJVkkrjBv73DqnYVmJq7dEi+xJEonjmzO1w6Be6qTvWKi4MXb3QiulS8dZwKeiK/sHqbahNoQwXu4AYXrNiU7OAKPZPxxXTREjSdqqtGdElZ6JkhD2XrDXkk3wqFHsmTChe7hsmzOyb+Ca+ti1TZMNqQ8pCKQ4QX8M4Wc7IZ/mvbyVz275YZLMHKwdtWEMcJ01aJUumNZAjB9mRpjiQitXM9N+WstlwURipSCEqUkuxC/fwH6sIF5opw9SMBlSLog2NDHeKVzYEz3S1COiBrpbHgPJSCk1Xf79QzXeiqO0H5tAyCM4TV6aDNwEVRWNf9F+En6jdB2YAKDoGiJ1/DnbGqJ1/DXYm3p0cwjbYZoryMdzyGmIQnoIxwEiP3wMKOeMG8uDcdw+HteiaDXy5is5Q20Kb0KhC6FYqE9oEgp1Wat4XkQvofJa5kEazDIxUUDplv5pasu+w42nY83uwExx2PIade7DTG+EdRb+OSkD7zX3sT8V0xu+ANu8a2x7UZko+MeiYiq2d4bXm/8FXmYdihnM/wrifn7EbVll20Imlge4PW1mzcfDee8H4br+RnXM5ToIk+e6xscDxTzH8l9j0pb88fQ849xOM+9Ec63/yy/2PkLKTDxj64JBKk6PiiZSaDAWeTtPI5B6NjJAqcQKP7wK/yEQJS4pvu51HHJI3hAGRu1PssZ8qwstUEb7OANRna4Et6WjMlfjDShotO9FYLj+OI1J38gFD3/k+nwYXj8BF2AhmYxHMPyqCcTyV41UlfhzHBHmAh6dKzK5P8Nx3escX1aqgoysIwGVG9xT6APxtmcNQbpSs1xu2L5447HU3F4e4hrXKoWj7dsuVNusb0/CbkDl0iJW9D83tQ9MWyhFc0d9hj+xM2+Eh2wMw64RZb5Vs1lwABl0Z1bFjb1H07jnSkf2jWDUcvO3dxMav5KrsuOmfjxBlGt/5dTTIiH1OItjubaiJ+p9eZcoHftH/24PxVe6914X3Kn9bOq+Y+s7Y+KLMd49CPeE7+3NJj94uebjfbjrF7g90IfJdmSbKdeqX6+RCaXAj/4GP+Wgx+IXgVPNnIfh5HUjfC8Fvbv3VkGJFtbZuWJMG3NWvnf1Tje2N3eRj5LriP+oYSbDHSIY8RZKJs29+jzwlE7VvcRd4jgOPUcyRd+MYxXyJA49QzJHjZYRhniLVKx1j7jt6UuR9NEUxf3c77aBF1U7BEFHduO9fRz04C54bPHzWkNfVBOUKsmVzFDiyZXNMbaY5NgnZ7ST0I6Q3C8gmzsYDBZrtTrfV4Af+gNYFAMG708/z7od0psgjt6ug8brfvozSxUO8SJbpPE/nx+P/Nl4QYw=="
        bp_str = "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"
        bp = Blueprint(bp_str)
        id = 0
        for entity in bp.entities:
            entity.id = str(id)
            id += 1

        g1 = FactoryCellGroup('g1')
        g2 = FactoryCellGroup('g2', name='test2', position=(0,25))
        # g1.entities = bp.entities
        
        bp2 = Blueprint()
        bp2.entities.append(g1)
        bp2.entities.append(g2)
        # g1.entities = bp.entities
        bp2.entities['g1'].entities = bp.entities
        bp2.entities['g2'].entities = bp.entities
        bp2.icons = bp.icons
        print(bp2.to_string())
        for entity in g1.entities:
            print(entity)

    def test123(self,path):
        file = open(path)
        bp_str = file.readline()
        # bp_str.rstrip('\n')
        # GRID bp
        bp_str = "0eNqdmt1u4jAQhd8l16Gyx7Ed8yqragU06kaiCQqh2qri3TcpPyplspyTS1ryceKZsY/H/szW20O16+qmz5afWb1pm322/PWZ7evXZrUd/9Z/7KpsmdV99ZblWbN6Gz91q3qbHfOsbl6qv9nSHp/zrGr6uq+r0/NfHz5+N4e3ddUNX7g+ue+HZ1//9IsvRJ7t2v3wVNuMPzWSUp59jMBjfgeRK2Rdvy6qbbXpu3qz2LXb6h4kcgYND1XDD67bQzdK8zEP7lmhO1Si+GmJBfmeToN4UokKCaQSr0EiqUSFlFfI5tC9Vy9TOsrTsJohYi91NwT3639eISby3aImyxpMlwRVV6EhLTleujAhXy+pFDafdQqb0FYtC8um9AQmgKl0rv1wGzLRkHCK27Mydwt1GrS8mSgXmz+rulmcp9R7cPF0RsuTv4VbDc5mv1XnBzFsSHQMnvJJHT+tvkWwODs9zlFDOiYkkiZDosVbilv4FLa8UP1Pqpaa4qksChw8UPB4gQ+5qqZBZJNSx1CFI8K9cmIzXtXoDKUxUhqdpeDhe1geLk9OGLjznHJ4vbEnagSY8OrjcCa8FHmcCZutiDPhiko4s4RjRAQJX4/wKBWGXZYRKL4LweNUsG7NqqavcDzmsTa4fgSPd4F7OSLegZ2bEWjkoRoGrhoh0iaxvgmAerhqHB5vD1eNw+Pt4apxeLw9XEMOD5TH1yAiUHANFUSg4BoqiEBFpulyEivmZ9NFcitWa7r4b4avXbe7tusVuReqBkjzfGzSfWww7DSsbpsD2wiYwAgyOuY/wxMcE75zXhDxC2x/QNSNfWD7AxOYMMs9i0Hcc4icwRX3uLpCyRlciJk4g4swo+EMLsS0VDNHisf78CicZ4ZkOtIzQ9CC9MwQ1JOeGYIG0jNDULZbIGrvKZY85rG2RHpmBFoa0jNDUHaRgaDCQzWMIz0zpK2g2oI/Z4ygIT1pwyGdgbThEDSSNhyClqQNh6CJtOEINBnShkNQS9pwCCqkDYegVPv60meWu7agVgOpYNeN+PiUIvlZvly87stTmNULBweAXo50jVzz2nIa2ea1rtEaw0548fHhijV2Vk8ce3VrZJ6t94itt8ZhhzfXfjiquqDOvZ3R4+VnHSWOQ4zEjb0lIBNH6ZE6S3cGOOY0JZvxE9rSrJO/+xH06ok/2zAQ/ZydvjowxWHb0U4/aaevD0xx6BsxTufQl2ImOGzGO30etWxveYrD7mGcnuWWXR8mOMLms9Pz8Nu9APyy1sBCb2tZYTcqo9Dn/HSPbfnt2luevVfd/uS8SlvEJNGHYUWzcjz+Az5/z8Y="
        bp_str2 = "0eJyVk0lqxDAQRe9SazXE8uxlrhFMkLqLToEtG0kOMUZ3jzzQNNpYXmms//hV/AVkN+GoSVloFqD7oAw0XwsYeirRrXd2HhEaIIs9MFCiX09aUAeOAakH/kGTuJYBKkuWcK8//plJGissDcrXjoOhbetVfdEtZzD7Jam90IM03vfHj0Nq/lZTL1F7ec9Fev7IYdKrfNE6FofgycYozgg8IJSxhN3DuYU0AFSxgMPBLT8jZAEhv0g4BeQBILvWo4g5FwEhuTrn8y6VAYJHI2InXQWEtF3DscWneUsbg1/UZtPgVZKVNS8zXtdp7Z10QqLPHny+fjv3D2crNyA="

        # poles bp
        # bp_str = "0eJyVkt1qxCAQhd9lrs2ymixbvexrLMsSkyEd8CcYUxqC776aLaUU2nSvRD3nfKMzK2gz4xjIRVArUOfdBOqywkSDa005i8uIoIAiWmDgWlt2moYKDXYxUFeN3iAkBuR6/ADF05UBukiR8BH2q4nB6Kes866QsrfiRwZLXk85r6eQxdvl8TNxubnZagyZkmtBGt60n0OhCFZfE3uGxf9JEj9I/ElOddpAfI9T/8Wx2NNs91Dy8GA1h91XNaVLW1PVtxlg8I5h2izihTdnKc6NkLKW+bNMqzFPBLx+qVO6A8Mnvng="
        
        # Labs bp
        # bp_str = "0eJy1ldtugzAMht/F10kFAUrhcq8xTRMHq4sGgZFQDVW8+5K2q+ja0ZCtVxzsfL/j2PEe8qrHtuNCQboHXjRCQvq8B8m3IqvMPzW0CClwhTUQEFltvnLMtCuMBLgo8RNSfyR3F1VZPlnBxhcCKBRXHI+aEzcCbSO1RWtomvam/ioiMOhlq8gwNFgaU9s1ZV8ovuNqoLV+r5AGBn5iD6+ir3PsThFehn+tEpxUoksV2SKW83hmg/ec8YEFnjnTwwldqqx4p1xI7JS2/b4J7yDzgxQtIM2C1hNQ1Wy5VLygxRtKRTv86PVzNjh6Exo7QeeZG5fcmXLWqJJ3WBzt4RU4cUilDdf3plm41WzfvWbawbHZrLrtHPV6ccX6Nv3G/sC3aTjKLitjkUBoewruN160JEcOW1jf2wL9h0qKl9zbLie9eejV6iePLVTmmTl6GLTpZJgT2GEnDwps44dxwuKQJUmQ+MQcFeopDU9n73H8AlTBmZE="
        bp = Blueprint(bp_str)
        bp2 = Blueprint(bp_str)
        bp3 = Blueprint(bp_str)
        bp4 = Blueprint(bp_str)
        bp5 = Blueprint(bp_str2)

        # new_id = 0
        # inserters = bp.find_entities_filtered(type='inserter')
        # for ins in inserters:
        #     ins.id = str(new_id)
        #     new_id += 1
        #     base_pos = ins.position
        #     pos1 = (base_pos['x'], base_pos['y']+1)
        #     nb = bp.find_entities_filtered(position=pos1)
        #     if(nb[0].type == 'logistic-container'): 
        #         nb[0].id = str(new_id)
        #         new_id += 1
        #         bp.add_circuit_connection('red', ins.id, nb[0].id)
        #     pos1 = (base_pos['x'], base_pos['y']-1)
        #     nb = bp.find_entities_filtered(position=pos1)
        #     if(nb[0].type == 'logistic-container'):
        #         nb[0].id = str(new_id)
        #         new_id += 1
        #         bp.add_circuit_connection('green', ins.id, nb[0].id)

        g1 = Group('g1')
        g2 = Group('g2')
        g3 = Group('g3')
        g4 = Group('g4')
        g5 = Group('g5')
        
        g1.position = (0,0)
        g2.position = (42,0)
        g3.position = (0,38)
        g4.position = (42,38)
        g5.position = (22,20)
        for entity in bp2.entities:
            g1.entities.append(entity)
        for entity in bp.entities:
            g2.entities.append(entity)
        for entity in bp3.entities:
            g3.entities.append(entity)
        for entity in bp4.entities:
            g4.entities.append(entity)
        for entity in bp5.entities:
            g5.entities.append(entity)
        # g1.entities = bp2.entities
        # g2.entities = bp.entities
        # g3.entities = bp3.entities
        # g4.entities = bp4.entities
        # g5.entities = bp5.entities

        bp8 = Blueprint()
        # for entity in bp.entities:
        #     bp8.entities.append(entity)

        bp8.icons = bp.icons
        bp8.entities = bp.entities.data
        print(bp8.to_string())

        for entity in g1.entities:
            entity.neighbours = None
        for entity in g2.entities:
            # entity.position['x'] += 42
            entity.neighbours = None
        for entity in g3.entities:
            # entity.position['x'] += 42
            # entity.position['y'] += 38
            entity.neighbours = None
        for entity in g4.entities:
            # entity.position['y'] += 38
            entity.neighbours = None
        for entity in g5.entities:
            # entity.position['x'] += 22
            # entity.position['y'] += 20
            entity.neighbours = None
        
        # bp.generate_power_connections()

        bp6 = Blueprint()
        bp6.entities.append(g1)
        bp6.entities.append(g2)
        bp6.entities.append(g3)
        bp6.entities.append(g4)
        bp6.entities.append(g5)
        g6 = Group('g6')
        g6.entities.append('inserter', tile_position=(0,0))
        g6.entities.append('inserter', tile_position=(1,0))
        g6.entities.append('inserter', tile_position=(2,0))
        # g6.entities.append('medium-electric-pole', position=(0,5))
        g7 = Group('g7')
        g7.position = (5,5)
        g7.entities.append('fast-inserter', tile_position=(0,1))
        g7.entities.append('fast-inserter', tile_position=(0,2))
        g7.entities.append('fast-inserter', tile_position=(0,3))

        bp6.entities.append(g6)
        bp6.entities.append(g7)
        bp6.icons = bp.icons
        
        print(bp6.to_string())

        bp6.generate_power_connections()

        print(123)

    def generateFactoryBlueprint(self, factory):
        print("hello")