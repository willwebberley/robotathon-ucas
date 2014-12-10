from rgkit import rg
from rgkit import comsc_bot

class Robot(comsc_bot.ComscBot):
	def act(self,game):
		
		##move from spawn points
		for location in rg.locs_around(self.location):
			if "spawn" not in rg.loc_types(location):
				return super(Robot, self).move_to_location(rg.CENTER_POINT)

		tr = 0
		for allrob in game.robots:
			if allrob.player_id!=self.player_id:
				if rg.dist(self.location,allrob.location)<=1:
					tr += 1

			##kill self if 2 or more enemies around
			if tr>= 2:
				return super(Robot, self).self_destruct()

			return super(Robot, self).attack_location(allrob.location)


			
		return super(Robot, self).move_towards(rg, rg.CENTER_POINT)

		if self.hp<10:
			return super(Robot, self).self_destruct()




		
