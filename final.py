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
        self.velocity = pygame.Vector2(0, 0)
        self.width, self.height = 50, 50
        self.rect = pygame.Rect(0, 0, self.width, self.height) 
        self.is_jumping = False
        self.hearts = 3
    
    def draw(self):
        draw_rect = pygame.Rect(
            self.position.x - camera_offset_x,
            self.position.y,
            self.width,
            self.height
        )
        pygame.draw.rect(screen, "Red", draw_rect)

    def jump(self):
        if not self.is_jumping:
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
        self.position += self.velocity
        
        # update collision rect 
        self.rect.x = self.position.x
        self.rect.y = self.position.y
        
        # reset ground state
        on_ground = False
        
        # check ground collisions
        for ground in grounds:
            ground_x = ground[0]  # Use WORLD x coordinate for collision
            ground_y = ground[1]
            ground_width = ground[2]
            ground_height = ground[3]
            
            ground_rect = pygame.Rect(ground_x, ground_y, ground_width, ground_height)
            
            # ignore other grounds if not colliding with player
            if self.rect.colliderect(ground_rect):
                # calculate overlap amounts
                overlap_top = ground_rect.top - self.rect.bottom
                overlap_bottom = ground_rect.bottom - self.rect.top
                overlap_left = ground_rect.left - self.rect.right
                overlap_right = ground_rect.right - self.rect.left
                
                # find the smallest overlap (indicates collision side)
                overlaps = {
                    "top": abs(overlap_top),
                    "bottom": abs(overlap_bottom),
                    "left": abs(overlap_left),
                    "right": abs(overlap_right)
                }
                min_overlap = min(overlaps, key=overlaps.get)
                
                # Handle collision based on side
                if min_overlap == "top" and self.velocity.y > 0:
                    # user landing on ground
                    self.position.y = ground_rect.top - self.height
                    self.velocity.y = 0
                    on_ground = True
                elif min_overlap == "bottom" and self.velocity.y < 0:
                    # hit bottom
                    self.position.y = ground_rect.bottom
                    self.velocity.y = 0
                elif min_overlap == "left":
                    # touched left side
                    self.position.x = ground_rect.left - self.width
                elif min_overlap == "right":
                    # touched right side
                    self.position.x = ground_rect.right
        
        self.is_jumping = not on_ground
    
        if self.position.x < 0:
            self.position.x = 0

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
        
        if player.rect.colliderect(adjusted_obstacle_rect) and not obstacle.touched:
            print(f"Obstacle hit at {obstacle.body.x}, {obstacle.body.y}\nPlayer Position: {player.position.xy}")
            player.hit()
            obstacle.hit()



    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()
