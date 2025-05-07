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
        adjusted_ground = ground.copy()
        adjusted_ground[0] -= camera_offset_x
        rect = pygame.Rect(*adjusted_ground)
        pygame.draw.rect(screen, "Green", rect)

    for obstacle in obstacles:
        if not obstacle.touched:
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
        self.rect.x = self.position.x - camera_offset_x
        self.rect.y = self.position.y
        pygame.draw.rect(screen, "Red", self.rect)

    def jump(self):
        if not self.is_jumping:  # only jump if not already jumping
            self.velocity.y = -15 
            self.is_jumping = True

    def move_right(self):
        self.velocity.x += 3
        self.position += self.velocity
        self.velocity.x = 0

    def move_left(self):
        self.velocity.x -= 3
        self.position += self.velocity
        self.velocity.x = 0

    def hit(self):
        self.hearts -= 1
        if self.hearts == 0:
            print("Player died!")
        print(f"Player hit! Hearts Left: {player.hearts}")

    def update(self):
        # apply gravity
        self.velocity.y += 0.8
        
        # store previous position for collision checks
        old_position = pygame.Vector2(self.position.x, self.position.y)
        
        # apply velocity to position
        self.position += self.velocity
        
        # boundary check (left side of world)
        if self.position.x < 0:
            self.position.x = 0
        
        # update rect position (world coordinates)
        self.rect.x = self.position.x
        self.rect.y = self.position.y

        self.check_ground_collisions(old_position)
        self.check_side_collisions(old_position)

        self.velocity.x = 0


    def check_ground_collisions(self, old_position):
        # Ground check (same as before but cleaned up)
        for ground in grounds:
            ground_rect = pygame.Rect(*ground)
            
            # standing on ground logic
            if (self.rect.bottom >= ground_rect.top and 
                old_position.y + self.rect.height <= ground_rect.top and
                self.rect.right > ground_rect.left and 
                self.rect.left < ground_rect.right):
                self.position.y = ground_rect.top - self.rect.height
                self.velocity.y = 0
                self.is_jumping = False
            
            # hitting ground from below logic
            elif (self.rect.top <= ground_rect.bottom and 
                  old_position.y >= ground_rect.bottom and
                  self.rect.right > ground_rect.left and 
                  self.rect.left < ground_rect.right):
                self.position.y = ground_rect.bottom
                self.velocity.y = 0

    def check_side_collisions(self, old_position):
        # Side collision check with ground
        for ground in grounds:
            ground_rect = pygame.Rect(*ground)
            
            # Moving right into a wall
            if (self.velocity.x > 0 and  # Moving right
                self.rect.left < ground_rect.right and
                old_position.x + self.rect.width <= ground_rect.left and  # Wasn't colliding before
                self.rect.bottom > ground_rect.top + 5 and  # Only collide if not just "grazing"
                self.rect.top < ground_rect.bottom - 5):
                self.position.x = ground_rect.left - self.rect.width
            
            # Moving left into a wall
            elif (self.velocity.x < 0 and  # Moving left
                  self.rect.right > ground_rect.left and
                  old_position.x >= ground_rect.right and  # Wasn't colliding before
                  self.rect.bottom > ground_rect.top + 5 and
                  self.rect.top < ground_rect.bottom - 5):
                self.position.x = ground_rect.right

player = Player()
camera_offset_x = max(0, player.position.x - screen.get_width() // 2)

class Obstacle:
    def __init__(self, position):
        self.position = position
        self.body = pygame.Rect(self.position.x, self.position.y, 25, 25)
        self.touched = False

    def draw(self):
        if not self.touched:
            adjusted_rect = self.body.copy()
            adjusted_rect.x -= camera_offset_x
            pygame.draw.rect(screen, "Black", adjusted_rect)

    def hit(self):
        self.touched = True

#convert every obstacle array into a new class obj
for obstacle in obstacles:
        X, Y = obstacle
        index = obstacles.index([X,Y])
        obstacle = Obstacle(pygame.Vector2(X, Y))
        obstacles[index] = obstacle
        obstacle.draw()

while running:
    # At the TOP of your game loop (BEFORE movement/rendering):
    camera_offset_x = player.position.x - screen.get_width() // 2
    camera_offset_x = max(0, camera_offset_x)  # Prevent left-edge overscroll

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
        # Create a temporary rect that accounts for camera offset
        adjusted_obstacle_rect = obstacle.body.copy()
        adjusted_obstacle_rect.x -= camera_offset_x
        
        if player.rect.colliderect(adjusted_obstacle_rect) and not obstacle.touched:
            player.hit()
            obstacle.hit()



    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()
