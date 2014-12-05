from rgkit import rg

class Robot:
    def act(self, game):
        if self.location == rg.CENTER_POINT:
            return ['suicide']
        return ['move', rg.toward(self.location, rg.CENTER_POINT)]
