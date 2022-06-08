import factory
# from draftsman import Blueprint, BlueprintBook
# from draftsman.classes.blueprint import Blueprint
# from draftsman.classes.blueprintbook import BlueprintBook
from draftsman.blueprintable import Blueprint
from draftsman.classes.group import Group
from draftsman import utils

class Blueprinter:
    def readBlueprint(self, path):
        file = open(path)
        # bp_str = file.readline()
        # bp_str.rstrip('\n')
        # GRID bp
        # bp_str = "0eNqdmt1u4jAQhd8l16Gyx7Ed8yqragU06kaiCQqh2qri3TcpPyplspyTS1ryceKZsY/H/szW20O16+qmz5afWb1pm322/PWZ7evXZrUd/9Z/7KpsmdV99ZblWbN6Gz91q3qbHfOsbl6qv9nSHp/zrGr6uq+r0/NfHz5+N4e3ddUNX7g+ue+HZ1//9IsvRJ7t2v3wVNuMPzWSUp59jMBjfgeRK2Rdvy6qbbXpu3qz2LXb6h4kcgYND1XDD67bQzdK8zEP7lmhO1Si+GmJBfmeToN4UokKCaQSr0EiqUSFlFfI5tC9Vy9TOsrTsJohYi91NwT3639eISby3aImyxpMlwRVV6EhLTleujAhXy+pFDafdQqb0FYtC8um9AQmgKl0rv1wGzLRkHCK27Mydwt1GrS8mSgXmz+rulmcp9R7cPF0RsuTv4VbDc5mv1XnBzFsSHQMnvJJHT+tvkWwODs9zlFDOiYkkiZDosVbilv4FLa8UP1Pqpaa4qksChw8UPB4gQ+5qqZBZJNSx1CFI8K9cmIzXtXoDKUxUhqdpeDhe1geLk9OGLjznHJ4vbEnagSY8OrjcCa8FHmcCZutiDPhiko4s4RjRAQJX4/wKBWGXZYRKL4LweNUsG7NqqavcDzmsTa4fgSPd4F7OSLegZ2bEWjkoRoGrhoh0iaxvgmAerhqHB5vD1eNw+Pt4apxeLw9XEMOD5TH1yAiUHANFUSg4BoqiEBFpulyEivmZ9NFcitWa7r4b4avXbe7tusVuReqBkjzfGzSfWww7DSsbpsD2wiYwAgyOuY/wxMcE75zXhDxC2x/QNSNfWD7AxOYMMs9i0Hcc4icwRX3uLpCyRlciJk4g4swo+EMLsS0VDNHisf78CicZ4ZkOtIzQ9CC9MwQ1JOeGYIG0jNDULZbIGrvKZY85rG2RHpmBFoa0jNDUHaRgaDCQzWMIz0zpK2g2oI/Z4ygIT1pwyGdgbThEDSSNhyClqQNh6CJtOEINBnShkNQS9pwCCqkDYegVPv60meWu7agVgOpYNeN+PiUIvlZvly87stTmNULBweAXo50jVzz2nIa2ea1rtEaw0548fHhijV2Vk8ce3VrZJ6t94itt8ZhhzfXfjiquqDOvZ3R4+VnHSWOQ4zEjb0lIBNH6ZE6S3cGOOY0JZvxE9rSrJO/+xH06ok/2zAQ/ZydvjowxWHb0U4/aaevD0xx6BsxTufQl2ImOGzGO30etWxveYrD7mGcnuWWXR8mOMLms9Pz8Nu9APyy1sBCb2tZYTcqo9Dn/HSPbfnt2luevVfd/uS8SlvEJNGHYUWzcjz+Az5/z8Y="
        # poles bp
        # bp_str = "0eJyVkt1qxCAQhd9lrs2ymixbvexrLMsSkyEd8CcYUxqC776aLaUU2nSvRD3nfKMzK2gz4xjIRVArUOfdBOqywkSDa005i8uIoIAiWmDgWlt2moYKDXYxUFeN3iAkBuR6/ADF05UBukiR8BH2q4nB6Kes866QsrfiRwZLXk85r6eQxdvl8TNxubnZagyZkmtBGt60n0OhCFZfE3uGxf9JEj9I/ElOddpAfI9T/8Wx2NNs91Dy8GA1h91XNaVLW1PVtxlg8I5h2izihTdnKc6NkLKW+bNMqzFPBLx+qVO6A8Mnvng="
        
        # Labs bp
        bp_str = "0eJy1ldtugzAMht/F10kFAUrhcq8xTRMHq4sGgZFQDVW8+5K2q+ja0ZCtVxzsfL/j2PEe8qrHtuNCQboHXjRCQvq8B8m3IqvMPzW0CClwhTUQEFltvnLMtCuMBLgo8RNSfyR3F1VZPlnBxhcCKBRXHI+aEzcCbSO1RWtomvam/ioiMOhlq8gwNFgaU9s1ZV8ovuNqoLV+r5AGBn5iD6+ir3PsThFehn+tEpxUoksV2SKW83hmg/ec8YEFnjnTwwldqqx4p1xI7JS2/b4J7yDzgxQtIM2C1hNQ1Wy5VLygxRtKRTv86PVzNjh6Exo7QeeZG5fcmXLWqJJ3WBzt4RU4cUilDdf3plm41WzfvWbawbHZrLrtHPV6ccX6Nv3G/sC3aTjKLitjkUBoewruN160JEcOW1jf2wL9h0qKl9zbLie9eejV6iePLVTmmTl6GLTpZJgT2GEnDwps44dxwuKQJUmQ+MQcFeopDU9n73H8AlTBmZE="
        bp = Blueprint(bp_str)
        bp2 = Blueprint(bp_str)

        new_id = 0
        inserters = bp.find_entities_filtered(type='inserter')
        for ins in inserters:
            ins.id = str(new_id)
            new_id += 1
            base_pos = ins.position
            pos1 = (base_pos['x'], base_pos['y']+1)
            nb = bp.find_entities_filtered(position=pos1)
            if(nb[0].type == 'logistic-container'): 
                nb[0].id = str(new_id)
                new_id += 1
                bp.add_circuit_connection('red', ins.id, nb[0].id)
            pos1 = (base_pos['x'], base_pos['y']-1)
            nb = bp.find_entities_filtered(position=pos1)
            if(nb[0].type == 'logistic-container'):
                nb[0].id = str(new_id)
                new_id += 1
                bp.add_circuit_connection('green', ins.id, nb[0].id)

        g1 = Group('g1', entities=bp2.entities)
        g2 = Group('g2', entities=bp.entities)

        for entity in g2.entities:
            entity.position['x'] += 9
        bp3 = Blueprint()
        # bp3.entities.append(g1)
        bp3.entities.append(g2)

        print(bp3.to_string())
        print(123)

    def generateFactoryBlueprint(self, factory):
        print("hello")