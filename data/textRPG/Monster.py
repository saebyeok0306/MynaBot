

class Monster:

    def __init__(self, lv:str, name:str, hp:int, atk:int, amr:int, dex:int):
        self.lv = lv
        self.name = name
        self.hp = hp
        self.atk = atk
        self.amr = amr
        self.dex = dex


slime = Monster("1 3", "슬라임", 100, 3, 0, 1)