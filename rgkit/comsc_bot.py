class ComscBot(object):
    def __init__(self):
        self.up = "up"
        self.down = "down"
        self.right = "right"
        self.left = "left"
    
    def move(self, direction):
        if direction == "up":
            return ['move', (self.location[0], self.location[1]-1)]
        elif direction == "down":
            return ['move', (self.location[0], self.location[1]+1)]
        elif direction == "left":
            return ['move', (self.location[0]-1, self.location[1])]
        elif direction == "right":
            return ['move', (self.location[0]+1, self.location[1])]
        else:
            raise Exception("Invalid move")
        
    def move_to_location(self, location):
        return ['move', location]
            
    def move_towards(self, rg, point):
        return ['move', rg.toward(self.location, point)]
                
    def attack(self, direction):
        if direction == "up":
            return ['attack', (self.location[0], self.location[1]-1)]
        elif direction == "down":
            return ['attack', (self.location[0], self.location[1]+1)]
        elif direction == "left":
            return ['attack', (self.location[0]-1, self.location[1])]
        elif direction == "right":
            return ['attack', (self.location[0]+1, self.location[1])]
        else:
            raise Exception("Invalid attack")
    
    def attack_location(self, location):
        return ['attack', location]
            
    def guard(self):
        return ['guard'];
    
    def self_destruct(self):
        return ['suicide'];
            
    
                