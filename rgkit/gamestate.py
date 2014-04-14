import random
from collections import defaultdict

from rgkit import rg
from rgkit.settings import settings, AttrDict


class GameState(object):
    def __init__(self, use_start=False, turn=0,
                 next_robot_id=0, seed=None, symmetric=False):
        if seed is None:
            seed = random.randint(0, settings.max_seed)
        self._seed = str(seed)
        self._spawn_random = random.Random(self._seed + 's')
        self._attack_random = random.Random(self._seed + 'a')

        self.robots = {}
        self.turn = turn
        self._next_robot_id = next_robot_id

        if use_start and settings.start is not None:
            for i, start in enumerate(settings.start):
                for loc in start:
                    self.add_robot(loc, i)

        self.symmetric = symmetric
        if symmetric:
            assert settings.player_count == 2
            self._get_spawn_locations = self._get_spawn_locations_symmetric
        else:
            self._get_spawn_locations = self._get_spawn_locations_random

    def add_robot(self, loc, player_id, hp=None, robot_id=None):
        if hp is None:
            hp = settings.robot_hp

        if robot_id is None:
            robot_id = self._next_robot_id
            self._next_robot_id += 1

        self.robots[loc] = AttrDict({
            'location': loc,
            'hp': hp,
            'player_id': player_id,
            'robot_id': robot_id
        })

    def remove_robot(self, loc):
        if self.is_robot(loc):
            del self.robots[loc]

    def is_robot(self, loc):
        return loc in self.robots

    def _get_spawn_locations_symmetric(self):
        def symmetric_loc(loc):
            return (settings.board_size - 1 - loc[0],
                    settings.board_size - 1 - loc[1])
        locs1 = []
        locs2 = []
        while len(locs1) < settings.spawn_per_player:
            loc = self._spawn_random.choice(settings.spawn_coords)
            sloc = symmetric_loc(loc)
            if loc not in locs1 and loc not in locs2:
                if sloc not in locs1 and sloc not in locs2:
                    locs1.append(loc)
                    locs2.append(sloc)
        return locs1 + locs2

    def _get_spawn_locations_random(self):
        # see http://stackoverflow.com/questions/2612648/reservoir-sampling
        locations = []
        per_player = settings.spawn_per_player
        count = per_player * settings.player_count
        n = 0
        for loc in settings.spawn_coords:
            n += 1
            if len(locations) < count:
                locations.append(loc)
            else:
                s = int(self._spawn_random.random() * n)
                if s < count:
                    locations[s] = loc
        self._spawn_random.shuffle(locations)
        return locations

    # actions = {loc: action}
    # all actions must be valid
    # delta = [AttrDict{
    #    'loc': loc,
    #    'hp': hp,
    #    'player_id': player_id,
    #    'loc_end': loc_end,
    #    'hp_end': hp_end
    #    'damage_caused' : damage_caused
    # }]
    def get_delta(self, actions, spawn=True):
        delta = {}

        def dest(loc):
            if actions[loc][0] == 'move':
                return actions[loc][1]
            else:
                return loc

        hitpoints = defaultdict(lambda: set())

        def stuck(loc):
            # we are not moving anywhere
            # inform others
            old_hitpoints = hitpoints[loc]
            hitpoints[loc] = set([loc])

            for rival in old_hitpoints:
                if rival != loc:
                    stuck(rival)

        for loc in self.robots:
            hitpoints[dest(loc)].add(loc)

        for loc in self.robots:
            if len(hitpoints[dest(loc)]) > 1 or (self.is_robot(dest(loc)) and
                                                 dest(loc) != loc and
                                                 dest(dest(loc)) == loc):
                # we've got a problem
                stuck(loc)

        # calculate new locations
        for loc, robot in self.robots.iteritems():
            if actions[loc][0] == 'move' and loc in hitpoints[loc]:
                new_loc = loc
            else:
                new_loc = dest(loc)

            delta[loc] = AttrDict({
                'loc': loc,
                'hp': robot.hp,
                'player_id': robot.player_id,
                'loc_end': new_loc,
                'hp_end': robot.hp,  # will be adjusted later
                'damage_caused': 0
            })

        # {loc: set(robots collided with loc}
        collisions = defaultdict(lambda: set())
        for loc in self.robots:
            for loc2 in hitpoints[dest(loc)]:
                collisions[loc].add(loc2)
                collisions[loc2].add(loc)

        # {loc: [
        #        damage_dealt_by_player_0 : {other_loc1 : damage, ... },
        #        damage_dealt_by_player_1 : {other_loc2 : damage, ... },
        # ]}
        damage_map = defaultdict(
            lambda: [{} for _ in xrange(settings.player_count)])

        for loc, robot in self.robots.iteritems():
            actor_id = robot.player_id

            if actions[loc][0] == 'attack':
                target = actions[loc][1]
                damage = self._attack_random.randint(
                    *settings.attack_range)
                damage_map[target][actor_id][loc] = damage

            if actions[loc][0] == 'suicide':
                another_id = (actor_id + 1) % settings.player_count
                damage_map[loc][another_id][loc] = settings.robot_hp

                damage = settings.suicide_damage
                for target in rg.locs_around(loc):
                    damage_map[target][actor_id][loc] = damage

        # apply damage
        for loc, delta_info in delta.iteritems():
            loc_end = delta_info.loc_end
            robot = self.robots[loc]
            is_guard = (actions[loc][0] == 'guard')
            # apply collision damage
            if not is_guard:
                damage = settings.collision_damage

                for other_loc in collisions[delta_info.loc]:
                    if robot.player_id != self.robots[other_loc].player_id:
                        other_delta = delta[other_loc]
                        if other_delta is not None:
                            other_delta.damage_caused += damage
                        delta_info.hp_end -= damage

            # apply other damage
            damage_taken = 0
            for player_id, damage_player_map in enumerate(damage_map[loc_end]):
                if player_id != robot.player_id:
                    for caused_loc, damage in damage_player_map.items():
                        damage_taken += damage

                        # ignore suicide self damage
                        if caused_loc != loc:
                            damage_caused = damage
                            if is_guard:
                                damage_caused /= 2

                            caused_delta = delta[caused_loc]
                            if caused_delta is not None:
                                caused_delta.damage_caused += damage_caused

            if is_guard:
                damage_taken /= 2

            delta_info.hp_end -= damage_taken

        if spawn:
            if self.turn % settings.spawn_every == 0:
                # clear bots on spawn
                for delta_info in delta.values():
                    loc_end = delta_info.loc_end

                    if loc_end in settings.spawn_coords:
                        delta_info.hp_end = 0

                # spawn bots
                locations = self._get_spawn_locations()
                for i in xrange(settings.spawn_per_player):
                    for player_id in xrange(settings.player_count):
                        loc = locations[player_id*settings.spawn_per_player+i]
                        delta[loc] = AttrDict({
                            'loc': loc,
                            'hp': 0,
                            'player_id': player_id,
                            'loc_end': loc,
                            'hp_end': settings.robot_hp,
                            'damage_caused': 0
                        })

        return delta.values()

    # delta = [AttrDict{
    #    'loc': loc,
    #    'hp': hp,
    #    'player_id': player_id,
    #    'loc_end': loc_end,
    #    'hp_end': hp_end
    # }]
    # returns new GameState
    def apply_delta(self, delta):
        new_state = GameState(settings,
                              next_robot_id=self._next_robot_id,
                              turn=self.turn + 1,
                              seed=self._spawn_random.randint(
                                  0, settings.max_seed),
                              symmetric=self.symmetric)

        for delta_info in delta:
            if delta_info.hp_end > 0:
                loc = delta_info.loc

                # is this a new robot?
                if delta_info.hp > 0:
                    robot_id = self.robots[loc].robot_id
                else:
                    robot_id = None

                new_state.add_robot(delta_info.loc_end, delta_info.player_id,
                                    delta_info.hp_end, robot_id)

        return new_state

    # actions = {loc: action}
    # all actions must be valid
    # returns new GameState
    def apply_actions(self, actions, spawn=True):
        delta = self.get_delta(actions, spawn)

        return self.apply_delta(delta)

    def get_scores(self):
        scores = [0 for _ in xrange(settings.player_count)]

        for robot in self.robots.itervalues():
            scores[robot.player_id] += 1

        return scores

    # export GameState to be used by a robot
    def get_game_info(self, player_id):
        game_info = AttrDict()

        game_info.robots = dict((loc, AttrDict(robot))
                                for loc, robot in self.robots.iteritems())
        for robot in game_info.robots.itervalues():
            if robot.player_id != player_id:
                del robot.robot_id

        game_info.turn = self.turn

        return game_info

    # actor = location
    # action = well, action
    def is_valid_action(self, actor, action):
        try:
            if len(str(action)) > settings.str_limit:
                return False

            if len(repr(action)) > settings.str_limit:
                return False

            if action[0] in ['move', 'attack']:
                return action[1] in rg.locs_around(
                    actor, filter_out=['invalid', 'obstacle'])
            elif action[0] in ['guard', 'suicide']:
                return True
            else:
                return False

        except:
            return False
