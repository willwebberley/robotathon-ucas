from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot):
	def act(self, game):
		if rg.loc_types(self.location) == "spawn":
 			return super(Robot, self).move_towards(rg, rg.CENTER_POINT)