import random


class Robot:
    def act(self, game):
        return random.choice((['guard'], ['suicide']))
