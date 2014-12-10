from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot):
 	def act(self, game):
 		if self.location != game.centre_location:
 			return super(Robot, self).move_towards(rg, game.centre_location)
 		else:
 			return super(Robot, self).move("left")
