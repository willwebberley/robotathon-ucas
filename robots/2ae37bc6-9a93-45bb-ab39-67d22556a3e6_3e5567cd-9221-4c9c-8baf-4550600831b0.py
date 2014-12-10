from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot): 
	def act(self, game):
		if self.location == rg.CENTER_POINT:
			return super(Robot, self).move(rg.CENTER_POINT)