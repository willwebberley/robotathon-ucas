from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot):
 	def act(self, game):
 		for location in rg.locs_around(self.location):
 			if "spawn" not in rg.loc_types(location):
 				return super(Robot, self).move_to_location(location)