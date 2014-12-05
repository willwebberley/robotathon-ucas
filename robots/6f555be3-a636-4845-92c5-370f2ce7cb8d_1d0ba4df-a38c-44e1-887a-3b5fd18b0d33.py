from rgkit import rg

class Robot:
    def act(self, game):
        return ['move', (self.location[0]-1, self.location[1])]
