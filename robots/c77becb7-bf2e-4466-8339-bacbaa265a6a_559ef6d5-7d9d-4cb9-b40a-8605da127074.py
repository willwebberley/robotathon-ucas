from rgkit import rg
from rgkit import comsc_bot
class Robot(comsc_bot.ComscBot):
    _acceptable_location_types = ["normal"]
    _move_number = 0
    def act(self, game):
        self._move_number = self._move_number + 1
        if self._move_number == 1:
            _move_from_spawnpoint(game); # Start moving away from the spawn-point
    
    def _move_from_spawnpoint(self, game):
        current_location = self.location
        for surrounding_location in rg.locs_around(current_location):
            if _is_feasible_location(surrounding_location):
                return super(Robot, self).move_towards(rg, surrounding_location, game) # TODO logic to stop diagonal moves
    
    def _is_feasible_location(self, location, game):
        location_type = rg.loc_types(location)
        return location_type in _acceptable_location_types