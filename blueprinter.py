import factory
from globals import *
from draftsman.classes.blueprint import Blueprint
from draftsman.classes.blueprintbook import BlueprintBook
# from draftsman.classes.blueprint import Blueprint
# from draftsman.classes.blueprintbook import BlueprintBook
# from draftsman.classes.group import Group
from draftsman.blueprintable import Blueprint, BlueprintBook
# from draftsman import utils
import sys

class Blueprinter:
    def __init__(self, bpb_path=EMPTY, factory=EMPTY):
        if(bpb_path is not EMPTY):
            bpb_file = open(bpb_path)
            # self.bpb_str = bpb_file.readline()
            self.bpb_str = "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"

            self.ub_book = BlueprintBook(self.bpb_str)
            # self.ub_book.load_from_string(self.bpb_str)
        else:
            self.ub_book = BlueprintBook()
        
        bp_str = "0eNqdmt1u4jAQhd8l16Gyx7Ed8yqragU06kaiCQqh2qri3TcpPyplspyTS1ryceKZsY/H/szW20O16+qmz5afWb1pm322/PWZ7evXZrUd/9Z/7KpsmdV99ZblWbN6Gz91q3qbHfOsbl6qv9nSHp/zrGr6uq+r0/NfHz5+N4e3ddUNX7g+ue+HZ1//9IsvRJ7t2v3wVNuMPzWSUp59jMBjfgeRK2Rdvy6qbbXpu3qz2LXb6h4kcgYND1XDD67bQzdK8zEP7lmhO1Si+GmJBfmeToN4UokKCaQSr0EiqUSFlFfI5tC9Vy9TOsrTsJohYi91NwT3639eISby3aImyxpMlwRVV6EhLTleujAhXy+pFDafdQqb0FYtC8um9AQmgKl0rv1wGzLRkHCK27Mydwt1GrS8mSgXmz+rulmcp9R7cPF0RsuTv4VbDc5mv1XnBzFsSHQMnvJJHT+tvkWwODs9zlFDOiYkkiZDosVbilv4FLa8UP1Pqpaa4qksChw8UPB4gQ+5qqZBZJNSx1CFI8K9cmIzXtXoDKUxUhqdpeDhe1geLk9OGLjznHJ4vbEnagSY8OrjcCa8FHmcCZutiDPhiko4s4RjRAQJX4/wKBWGXZYRKL4LweNUsG7NqqavcDzmsTa4fgSPd4F7OSLegZ2bEWjkoRoGrhoh0iaxvgmAerhqHB5vD1eNw+Pt4apxeLw9XEMOD5TH1yAiUHANFUSg4BoqiEBFpulyEivmZ9NFcitWa7r4b4avXbe7tusVuReqBkjzfGzSfWww7DSsbpsD2wiYwAgyOuY/wxMcE75zXhDxC2x/QNSNfWD7AxOYMMs9i0Hcc4icwRX3uLpCyRlciJk4g4swo+EMLsS0VDNHisf78CicZ4ZkOtIzQ9CC9MwQ1JOeGYIG0jNDULZbIGrvKZY85rG2RHpmBFoa0jNDUHaRgaDCQzWMIz0zpK2g2oI/Z4ygIT1pwyGdgbThEDSSNhyClqQNh6CJtOEINBnShkNQS9pwCCqkDYegVPv60meWu7agVgOpYNeN+PiUIvlZvly87stTmNULBweAXo50jVzz2nIa2ea1rtEaw0548fHhijV2Vk8ce3VrZJ6t94itt8ZhhzfXfjiquqDOvZ3R4+VnHSWOQ4zEjb0lIBNH6ZE6S3cGOOY0JZvxE9rSrJO/+xH06ok/2zAQ/ZydvjowxWHb0U4/aaevD0xx6BsxTufQl2ImOGzGO30etWxveYrD7mGcnuWWXR8mOMLms9Pz8Nu9APyy1sBCb2tZYTcqo9Dn/HSPbfnt2luevVfd/uS8SlvEJNGHYUWzcjz+Az5/z8Y="
        test = Blueprint(bp_str)
        print(test)
        for bp in self.ub_book.blueprints:
            print(bp)

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