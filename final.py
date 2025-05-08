# Example file showing a circle moving on screen
import pygame
import json
import random
from datetime import *
import time
# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
current_lvl = 0
game_active = True
dead = False
# due to index (really 3)
MAX_LVL = 2
# time when game stopped being active
timed = None

#FONTS
font_name = "./assets/fonts/Pixel.ttf"
font_large = pygame.font.Font(font_name, 72)  # for title/header text
font_medium = pygame.font.Font(None, 48)  # for button text

#SOUNDS
death_sound = pygame.mixer.Sound("assets/sounds/death.mp3")
hits_sound = [pygame.mixer.Sound("assets/sounds/hit_1.mp3"), pygame.mixer.Sound("assets/sounds/hit_2.mp3"), pygame.mixer.Sound("assets/sounds/hit_3.mp3")]
# ranges from 0.0-1.0
DEFAULT_VOL = 0.15

#IMAGES
bg_image = pygame.image.load("assets/images/background.jpg").convert_alpha()

land_img = pygame.image.load("assets/images/land.png").convert_alpha()

heart_img = pygame.image.load("assets/images/heart.png").convert_alpha()
heart_img = pygame.transform.scale(heart_img, (50, 50)) 

obstacle_img = pygame.image.load("assets/images/obstacle.png").convert_alpha()
obstacle_img = pygame.transform.scale(obstacle_img, (30, 30)) 

player_img = pygame.image.load("assets/images/player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (65, 65)) 



with open("assets/levels.json", "r") as f:
    levels_json = json.load(f) # load entire json file into variable

def level_info(num, info):
    level = levels_json["levels"][num]
    valid_info = ["start_pos", "obstacles", "goal", "ground"]
    if not (info in valid_info):
        return SyntaxError
    
    return level[f"{info}"]

obstacles = [*level_info(current_lvl, "obstacles")]
grounds = [*level_info(current_lvl, "ground")]

def draw_win_screen(time, current_lvl):
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA).convert_alpha()
    overlay.fill((0, 0, 0, 128)) 
    screen.blit(overlay, (0, 0))

    header_text = font_large.render(f"Congrats!", True, (255, 50, 50))
    timer_text = font_medium.render(str(time)[3:7], True, (255, 255, 255))

    header_rect = header_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 150))
    timer_rect = timer_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 100))

    screen.blit(header_text, header_rect)
    screen.blit(timer_text, timer_rect)

    # button dimensions
    button_width = 200
    button_height = 60
    spacing = 40  # space between buttons

    center_x = screen.get_width() // 2
    center_y = screen.get_height() // 2

    buttons = []

    # Restart button - left
    restart_rect = pygame.Rect(center_x - button_width - spacing//2, center_y + 50, button_width, button_height)
    pygame.draw.rect(screen, (50, 50, 50), restart_rect)
    pygame.draw.rect(screen, (255, 255, 255), restart_rect, 2)
    restart_text = font_medium.render("Restart", True, (255, 255, 255))
    restart_text_rect = restart_text.get_rect(center=restart_rect.center)
    screen.blit(restart_text, restart_text_rect)
    buttons.append(restart_rect)

    # Next Level button - right (only if not on final level)
    next_level_rect = None
    if current_lvl < MAX_LVL:
        next_level_rect = pygame.Rect(center_x + spacing//2, center_y + 50, button_width, button_height)
        pygame.draw.rect(screen, (50, 50, 50), next_level_rect)
        pygame.draw.rect(screen, (255, 255, 255), next_level_rect, 2)
        next_text = font_medium.render("Next Level", True, (255, 255, 255))
        next_text_rect = next_text.get_rect(center=next_level_rect.center)
        screen.blit(next_text, next_text_rect)
        buttons.append(next_level_rect)

    return buttons


def draw_death_screen():
    # Dark overlay
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA).convert_alpha()
    overlay.fill((0, 0, 0, 128))  # RGBA - last value (180) is alpha/transparency
    screen.blit(overlay, (0, 0))
    
    # "You Died!" text
    death_text = font_large.render("YOU DIED!", True, (255, 50, 50))
    text_rect = death_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 100))
    screen.blit(death_text, text_rect)
    
    # Restart button
    button_rect = pygame.Rect(screen.get_width()//2 - 100, screen.get_height()//2 + 50, 200, 60)
    pygame.draw.rect(screen, (50, 50, 50), button_rect)
    pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)  # White border
    
    button_text = font_medium.render("Restart", True, (255, 255, 255))
    button_text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, button_text_rect)
    
    return button_rect 

def draw_UI(player):
    screen.blit(bg_image, (0,0))
    for i in range(player.hearts):
        screen.blit(heart_img, (20 + i * 60, 10))

# ground 
def tile_land_image(surface, tile, x, y, width):
    tile_w = tile.get_width()
    tile_h = tile.get_height()
    num_tiles = width // tile_w
    remainder = width % tile_w

    # Draw full tiles
    for i in range(num_tiles):
        surface.blit(tile, (x + i * tile_w, y - tile_h))

    # Draw cropped tile at the end if needed
    if remainder > 0:
        # crop the tile
        cropped_tile = tile.subsurface((0, 0, remainder, tile_h))
        # place the cropped tile
        surface.blit(cropped_tile, (x + num_tiles * tile_w, y - tile_h))

goal = level_info(current_lvl, "goal")

def draw_game():
    global land_img

    #goal draw
    x, y, width, _ = goal
    x -= camera_offset_x
    tile_land_image(screen, land_img, x, y, width)

    for ground in grounds:
        adjusted_ground = ground.copy()
        adjusted_ground[0] -= camera_offset_x
        rect = pygame.Rect(*adjusted_ground)

        x, y, width, _ = adjusted_ground

        tile_land_image(screen, land_img, x, y + 35, width)
        # pygame.draw.rect(screen, "Green", rect)
    

    for obstacle in obstacles:
        if not obstacle.touched:
            obstacle.draw() 

class Player:
    def __init__(self, level=1):
        self.level = level
        self.starting_point = level_info(level, "start_pos")
        self.position = pygame.Vector2(*self.starting_point)
        self.velocity = pygame.Vector2(0, 0)
        self.width, self.height = 60, 60
        self.rect = pygame.Rect(0, 0, self.width, self.height) 
        self.is_jumping = False
        self.hearts = 10
        self.has_moved = False
    
    def draw(self):
        draw_rect = pygame.Rect(
            self.position.x - camera_offset_x,
            self.position.y,
            self.width,
            self.height
        )
        # pygame.draw.rect(screen, "Red", draw_rect)
        screen.blit(player_img, (draw_rect.x, draw_rect.y - 5))

    def jump(self):
        if not self.has_moved:
            self.has_moved = True
        if not self.is_jumping:
            self.velocity.y = -15 
            self.is_jumping = True

    def move_right(self):
        if not self.has_moved:
            self.has_moved = True
        self.velocity.x += 3
        self.position += self.velocity
        self.velocity.x = 0

    def move_left(self):
        if not self.has_moved:
            self.has_moved = True
        self.velocity.x -= 3
        self.position += self.velocity
        self.velocity.x = 0
    
    def hit(self):
        self.hearts -= 1
        hit_sound = random.choice(hits_sound)
        if self.hearts == 0:
            return
        hit_sound.set_volume(DEFAULT_VOL)
        hit_sound.play()

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
                    self.position.y = ground_rect.bottom + 5
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
        
        # falls out the map
        if self.position.y > screen.get_height() + 1000:
            self.hearts = 0
            death_sound.set_volume(DEFAULT_VOL)
            death_sound.play()

player = Player(current_lvl)
camera_offset_x = max(0, player.position.x - screen.get_width() // 2)

def update_timer(time_started):
    if time_started == None:
        return
    current_time = str(datetime.now() - time_started + penalty_time)
    timer_text = font_large.render(current_time[3:7], True, (255, 50, 50))
    # text_rect = timer_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 100))
    screen.blit(timer_text, (screen.get_width() - 200, 50))

class Obstacle:
    def __init__(self, position):
        self.position = position
        self.body = pygame.Rect(self.position.x, self.position.y, 25, 25)
        self.touched = False

    def draw(self):
        if not self.touched:
            adjusted_rect = self.body.copy()
            adjusted_rect.x -= camera_offset_x
            # pygame.draw.rect(screen, "White", adjusted_rect)
            screen.blit(obstacle_img, (adjusted_rect.x, adjusted_rect.y))

    def hit(self):
        self.touched = True

def obstacle_to_class():
    #convert every obstacle array into a new class obj
    for obstacle in obstacles:
            X, Y = obstacle
            index = obstacles.index([X,Y])
            obstacle = Obstacle(pygame.Vector2(X, Y))
            obstacles[index] = obstacle
            obstacle.draw()

obstacle_to_class()
timer = None
penalty_time = timedelta(0)

while running:

    # events
    for event in pygame.event.get():
        # pygame quit event
        if event.type == pygame.QUIT:
            running = False
        
        # click event
        if event.type == pygame.MOUSEBUTTONDOWN and not game_active:
            mouse_pos = pygame.mouse.get_pos()
            if dead:
                # button clicked at pos of button
                if button_rect.collidepoint(mouse_pos):
                    # Reset game
                    game_active = True
                    timer = None
                    penalty_time = timedelta(0)
                    player = Player(current_lvl)  # Create new player
                    obstacles = [*level_info(current_lvl, "obstacles")]
                    # Reset obstacles 
                    obstacle_to_class()
                    camera_offset_x = max(0, player.position.x - screen.get_width() // 2)
            else:
                for i, won_button in enumerate(won_buttons):
                    if won_button.collidepoint(mouse_pos) and i == 0:
                        # restart button
                        game_active = True
                        dead = False
                        timer = None
                        penalty_time = timedelta(0)
                        player = Player(current_lvl)  # Create new player
                        obstacles = [*level_info(current_lvl, "obstacles")]
                        # Reset obstacles 
                        obstacle_to_class()
                        camera_offset_x = max(0, player.position.x - screen.get_width() // 2)
                    elif won_button.collidepoint(mouse_pos) and i == 1:
                        #next level
                        current_lvl += 1
                        game_active = True
                        dead = False
                        timer = None
                        penalty_time = timedelta(0)
                        player = Player(current_lvl)  # Create new player
                        obstacles = [*level_info(current_lvl, "obstacles")]
                        # Reset obstacles 
                        obstacle_to_class()
                        camera_offset_x = max(0, player.position.x - screen.get_width() // 2)
    keys = pygame.key.get_pressed()

    if game_active:
        camera_offset_x = player.position.x - screen.get_width() // 2
        camera_offset_x = max(0, camera_offset_x)  # prevent left-edge overscroll


        draw_UI(player=player)
        draw_game()
        update_timer(timer)



        if keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]:
            if player.has_moved == False:
                timer = datetime.now()
            player.jump()
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            if player.has_moved == False:
                timer = datetime.now()
            player.move_right()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            if player.has_moved == False:
                timer = datetime.now()
            player.move_left()
        if keys[pygame.K_ESCAPE]:
            running = False

        player.update() # gravity and physics check every frame
        player.draw()

        # goal collision check
        goal_rect = pygame.Rect(*goal)
        if player.rect.colliderect(goal_rect):
            # user won the level
            timed = str(datetime.now() - timer + penalty_time)
            game_active = False
            dead = False
            continue
            

        for obstacle in obstacles:
            adjusted_obstacle_rect = obstacle.body.copy()
            
            if player.rect.colliderect(adjusted_obstacle_rect) and not obstacle.touched:
                penalty_time += timedelta(seconds=10)
                if player.hearts - 1 <= 0:
                    death_sound.set_volume(DEFAULT_VOL)
                    death_sound.play()
                player.hit()
                obstacle.hit()

        if player.hearts <= 0:
            game_active = False        
            dead = True
    else:
        # for background purposes
        draw_UI(player)
        player.draw()
        draw_game()
        
        if dead:
            # user dead at level
            button_rect = draw_death_screen()
        else:
            won_buttons = draw_win_screen(timed, current_lvl)

    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()