from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot): 
	def act(self, game):
		if self.location[0] == rg.CENTER_POINT[0]:
			return super(Robot, self).move(rg.CENTER_POINT)