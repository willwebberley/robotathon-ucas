from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot):
	def act(self, game):
		if not "spawn" in rg.loc_types(self.location):
			return super(Robot, self).move("left")
		else:
			if self.hp > 10:
				return super(Robot, self).guard()
			else:
				return super(Robot, self).self_destruct()
