from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot):
    
    def act(self, game):
        #return ['move', (self.location[0]-1, self.location[1])]
        return super(Robot, self).move("left")