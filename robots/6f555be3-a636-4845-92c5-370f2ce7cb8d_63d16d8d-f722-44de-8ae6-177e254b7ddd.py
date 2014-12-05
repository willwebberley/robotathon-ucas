from rgkit import rg
from rgkit import comsc_bot

class Robot(comsc_bot.ComscBot):
    def __init__(self):
        self.move = 0
        
    def act(self, game):
        self.move += 1
        return super().move("dafs")
