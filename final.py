# Example file showing a circle moving on screen
import pygame
import json
import math
from datetime import *
import time
# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
current_lvl = 0
# last_jumped = datetime(1990, 1, 1)

with open("assets/levels.json", "r") as f:
    levels_json = json.load(f) # load entire json file into variable

def level_info(num, info):
    level = levels_json["levels"][num - 1]
    valid_info = ["start_pos", "obstacles", "goal", "ground"]
    if not (info in valid_info):
        return SyntaxError
    
    return level[f"{info}"]

obstacles = [*level_info(current_lvl, "obstacles")]
grounds = [*level_info(current_lvl, "ground")]

def draw_game():
    for ground in grounds:
        rect = pygame.Rect(*ground)
        pygame.draw.rect(screen, "green", rect)
    for obstacle in obstacles:
            obstacle.draw()
    
class Obstacle:
    def __init__(self, position):
        self.position = position
        self.body = pygame.Rect(self.position.x, self.position.y, 25, 25)
        self.touched = False

    def draw(self):
        if self.touched == False:
            self.body.x = self.position.x
            self.body.y = self.position.y
            pygame.draw.rect(screen, "Blue", self.body)

    def hit(self):
        self.touched = True

#convert every obstacle array into a new class obj
for obstacle in obstacles:
        X, Y = obstacle
        index = obstacles.index([X,Y])
        obstacle = Obstacle(pygame.Vector2(X, Y))
        obstacles[index] = obstacle
        obstacle.draw()
class Player:
    def __init__(self, level=1):
        self.starting_point = level_info(level, "start_pos")
        self.position = pygame.Vector2(*self.starting_point)
        self.velocity = pygame.Vector2(0, 0)  # Track movement speed
        self.rect = pygame.Rect(self.position.x, self.position.y, 50, 50)
        self.is_jumping = False
        self.hearts = 3
    
    def draw(self):
        self.rect.x = self.position.x
        self.rect.y = self.position.y
        pygame.draw.rect(screen, "Red", self.rect)

    def jump(self):
        if not self.is_jumping:  # only jump if not already jumping
            self.velocity.y = -15 
            self.is_jumping = True

    def move_right(self):
        self.velocity.x += 5
        self.position += self.velocity
        self.velocity.x = 0

    def move_left(self):
        self.velocity.x -= 5
        self.position += self.velocity
        self.velocity.x = 0

    def hit(self):
        self.hearts -= 1
        if self.hearts == 0:
            print("Player died!")
        print(f"Player hit! Hearts Left: {player.hearts}")

    def update(self):
        # apply gravity velocity
        self.velocity.y += .8
        self.position += self.velocity
        # check to see if not hitting land above
        
        # ground check 
        for ground in reversed(grounds):
            # ground[0] = x_pos
            # ground[1] = y_pos
            # ground[2] = width
            # ground[3] = height

            # this handles ground bottom physics, making sure user doesn't go through the bottom of ground
            if (self.position.y - ground[1] <= 100 and self.position.y - ground[1] > 0) and ((self.position.x >= ground[0] - 50) and (self.position.x <= ground[0] + ground[2])):
                self.velocity.y = 0
                self.position.y = ground[1] + ground[3]

            # make sure the ground can allow the user to stand
            if (self.position.y >= ground[1] - 50 and self.position.y <= ground[1] + 50) and ((self.position.x >= ground[0] - 50) and (self.position.x <= ground[0] + ground[2])):
                self.position.y = ground[1] - 50
                self.velocity.y = 0
                self.is_jumping = False                


player = Player()

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        player.jump()
    if keys[pygame.K_d]:
        player.move_right()
    if keys[pygame.K_a]:
        player.move_left()
    if keys[pygame.K_ESCAPE]:
        running = False

    
    player.update() # gravity check to make sure user isn't floating
    player.draw()
    draw_game()

    for obstacle in obstacles:
        # if player rect touches obstacle and obstacle has not been hit
        if player.rect.colliderect(obstacle.body) and not obstacle.touched:
            # run hit methods
            player.hit()
            obstacle.hit()



    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()