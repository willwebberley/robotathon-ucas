from rgkit import rg
from rgkit import comsc_bot

class Robot(comsc_bot.ComscBot):
    self.move = 0
    def act(self, game):
        self.move += 1
        if self.move %2 == 0:
            return ['move', (self.location[0]-1, self.location[1])]
        if self.move %3 == 0:
            return ['attack', (self.location[0]-1, self.location[1])]
        else:
            return ['guard']
