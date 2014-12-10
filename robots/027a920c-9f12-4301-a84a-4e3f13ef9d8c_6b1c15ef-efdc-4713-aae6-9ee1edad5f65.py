from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot):
	def act (self, game):
		for robot in game.robots:
			if robot.player_id != self.player_id:
				if rg.dist(self.location, robot.location) <= 1:
					return super(Robot, self).attack_location(robot.location)