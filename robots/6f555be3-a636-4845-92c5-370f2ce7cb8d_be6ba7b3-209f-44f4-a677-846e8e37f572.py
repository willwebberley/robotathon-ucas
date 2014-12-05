from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot):
   def act(self, game):
      if self.hp > 50:
         return super(Robot, self).attack("left")
      else:
         return super(Robot, self).move("down")
