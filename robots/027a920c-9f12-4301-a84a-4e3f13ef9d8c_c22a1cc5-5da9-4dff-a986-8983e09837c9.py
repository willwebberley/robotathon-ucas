from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot):
	def act (self, game):
		return super(Robot, self).move_towards(rg, rg.CENTER_POINT)
		for robot in game.robots:
			if robot.player_id != self.player_id:
				if rg.dist(self.location, robot.location) <= 1:
					return super(Robot, self).attack_location(robot.location)
					if self.hp <= 10:
						return super(Robot, self).self_destruct()
						if self.location == rg.CENTER_POINT:
							return super(Robot, self).self_destruct()