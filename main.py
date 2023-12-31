import pygame
import time
import os
import random
pygame.font.init()
pygame.mixer.init(44100, 0)


# How big our window will be. Adjust according to resolution size.
WIDTH, HEIGHT = 850, 850
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SpaceGame")

# Sound when player shoots
sound = pygame.mixer.Sound("playerlaser.wav")
my_sound = pygame.mixer.Sound(sound)

# When player gets hit
hit = pygame.mixer.Sound("playerhit.wav")
player_hit = pygame.mixer.Sound(hit)

# Music loop throughout game
music = pygame.mixer.Sound("gamemusic.wav")
game_music = pygame.mixer.Sound(music)

# Sound when enemy shoots
pew = pygame.mixer.Sound("enemylaser.wav")
enemy_laser = pygame.mixer.Sound(pew)

# Sound when enemy dies
ed = pygame.mixer.Sound("enemydeath.wav")
enemy_death = pygame.mixer.Sound(ed)

# End game sound
end = pygame.mixer.Sound("endgame.wav")
end_game = pygame.mixer.Sound(end)

"""Assets can be downloaded and directed to be whatever you want. 
This is a simple design for game design practice."""

# Load all images by directing to assets and specifying which asset

# All enemies
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background image
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    
    def move(self, vel):
        self.y += vel
    
    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)
    
    def collision(self, obj):
        return collide(obj, self)
    


class Ship: # Allows to make objects and instances of ships to give attributes
    COOLDOWN = 10
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
                player_hit.play()

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
    
    # Values to establish borders in windows to keep player within perimeter
    def get_width(self):
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img) # Mask is used to establish a precise hitbox for laser contact
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            
            
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)
                        enemy_death.play()

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREED_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100): 
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    
    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

            if self.x >= 0 and self.x <= WIDTH and self.y >= 0 and self.y <= HEIGHT:
                if laser.x >= 0 and laser.x <= WIDTH and laser.y >= 0 and laser.y <= HEIGHT:
                    enemy_laser.play()
            else:
                pass


def collide(obj1, obj2): # Registers pixel collision without unproportionally large hitbox 
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None



# Game loop
def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)
    game_music.play()


    enemies = []

    wave_length = 5

    enemy_vel = 1

    player_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    laser_vel = 10

    def redraw_window():
        WIN.blit(BG, (0,0))

        # Draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        # Be able to ensure that text is precisely positioned no matter the window size
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("Get Rekt LMAO", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
            end_game.play()

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0: # Enemy spawn condition
            level += 1 # Level increment upon victory
            wave_length += 5 # Adds enemies as levels increment
            for i in range(wave_length): # Provides random spawn points/colors for enemy ships
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)


        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: # Loop to stop running by QUIT function in order to close window 
                run = False

        keys = pygame.key.get_pressed() # Setting up keybinds for fluid movement
        if keys[pygame.K_a] and player.x - player_vel > 0: # Left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # Right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # Up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 10 < HEIGHT: # Down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
            my_sound.play()

        for enemy in enemies:  
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 120) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                enemy_death.play()

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        
        player.move_lasers(-laser_vel, enemies) # Making laser_vel negative will shoot the laser up
        
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 30)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse button to begin", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))

        pygame.display.update()
        for event in pygame.event.get():
           if event.type == pygame.QUIT:
               run = False
           if  event.type == pygame.MOUSEBUTTONDOWN:
               main()

    pygame.quit()



main_menu()            