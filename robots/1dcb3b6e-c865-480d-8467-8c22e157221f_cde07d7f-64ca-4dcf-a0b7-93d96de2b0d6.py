from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot):
 	def act(self, game):
 		if self.location == rg.CENTER_POINT:
 			return super(Robot, self).self_destruct()
 		return super(Robot, self).move_towards(rg, rg.CENTER_POINT)
