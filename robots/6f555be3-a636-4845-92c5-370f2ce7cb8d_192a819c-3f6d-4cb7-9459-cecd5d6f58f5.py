from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot):
    def act(self, game):
        if self.location == rg.CENTER_POINT:
            return ['guard']

        # if there are enemies around, attack them
        for bot in game.robots:
            print bot.player_id
            #if bot.player_id != self.player_id:
            #    if rg.dist(loc, self.location) <= 1:
            #        return ['attack', loc]

        # move toward the center
        return ['move', rg.toward(self.location, rg.CENTER_POINT)]