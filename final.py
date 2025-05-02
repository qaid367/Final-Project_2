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
last_jumped = datetime(1990, 1, 1)

with open("assets/levels.json", "r") as f:
    levels_json = json.load(f) # load entire json file into variable

def level_info(num, info):
    level = levels_json["levels"][num - 1]
    valid_info = ["start_pos", "obstacles", "goal"]
    if not (info in valid_info):
        return SyntaxError
    
    return level[f"{info}"]

class Player:
    def __init__(self, level=1):
        self.starting_point = level_info(level, "start_pos")
        self.position = pygame.Vector2(*self.starting_point)
        self.velocity = pygame.Vector2(0, 0)  # Track movement speed
        self.rect = pygame.Rect(self.position.x, self.position.y, 50, 50)
        self.is_jumping = False
    
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


    def update(self):
        # Apply gravity
        self.velocity.y += .6
        # Update position
        self.position += self.velocity

        # Simple ground check (adjust 720 to your ground level)
        if self.position.y >= 720 - 50:
            self.position.y = 720 - 50
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
    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()