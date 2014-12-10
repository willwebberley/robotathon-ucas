from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot):
	def act(self, game):
		return super(Robot, self).move_towards(rg, rg.CENTER_POINT)
		return super(Robot, self).attack("right")
		return super(Robot, self).attack("left")

		if self.hp < 10:
			return super(Robot, self).self_destruct()

		if self.hp < 20:
			self.guard

			

