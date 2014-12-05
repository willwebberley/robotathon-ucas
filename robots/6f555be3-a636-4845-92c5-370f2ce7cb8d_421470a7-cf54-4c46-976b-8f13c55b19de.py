from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot):
    def act(self, game):
        if self.location == rg.CENTER_POINT:
            return super(Robot, self).guard()

        for bot in game.robots:
            if bot.player_id != self.player_id:
                if rg.dist(bot.location, self.location) <= 1:
                    return super(Robot, self).attack_location(bot.location)

        return super(Robot, self).move_towards(rg, rg.CENTER_POINT)