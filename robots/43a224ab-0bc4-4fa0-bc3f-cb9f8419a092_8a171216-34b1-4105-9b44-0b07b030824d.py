from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot):
	def act(self, game):
		if "spawn" in rg.loc_types(self.location):
			return super(Robot, self).move_towards(rg, rg.CENTER_POINT)
		else:
			if self.hp > 10:
				return super(Robot, self).guard()
			else:
				return super(Robot, self).self_destruct()