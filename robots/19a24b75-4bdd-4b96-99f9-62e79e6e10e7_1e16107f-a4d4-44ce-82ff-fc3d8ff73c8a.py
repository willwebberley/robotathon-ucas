from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot):
	def act(self,game):

		for robot in game.robots:
			if robot.player_id != self.player_id:
				if rg.dist(self.location, robot.location) <= 1:
					for location in game.get_surrounding_location(self.location):
						if location.get_location_types() is "normal":
							return super(Robot, self).move_towards(rg, location)




