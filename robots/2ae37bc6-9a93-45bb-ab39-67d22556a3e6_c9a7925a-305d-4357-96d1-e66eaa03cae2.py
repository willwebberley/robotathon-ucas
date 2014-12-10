from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot): 
	def act(self, game):
		if self.location != rg.CENTER_POINT:
			return super(Robot, self).move_towards(rg, rg.CENTER_POINT)
		if self.location == rg.CENTER_POINT:
			return super(Robot, self).self_destruct()
		for robot in game.robots:
			if robot.player_id != self.player_id:
				if self.hp < 20:
					return super(Robot, self).move_towards(rg, robot.location)
					return super(Robot, self).guard()
				else:
					return super(Robot, self).attack_location(robot.location)
				
					
