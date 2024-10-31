import os
import random
import math
import pygame as py
from os import listdir
from os.path import isfile, join

from load_sprite_sheets import load_sprite_sheets
import entities.Koopa as Koopa

from classes.Menu import Menu

py.init()

py.display.set_caption("tiSon n' Naomi's Bizzare Adventures")

# global variables
WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VELO = 5

# window
window = py.display.set_mode((WIDTH, HEIGHT))

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = py.image.load(path).convert_alpha()
    surface = py.Surface((size, size), py.SRCALPHA, 32)
    rect = py.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return py.transform.scale2x(surface)

# player class
class Player(py.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = py.Rect(x, y, width, height)
        self.x_velo = 0
        self.y_velo = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.score = 0 # total score of the player

    def increase_score(self, points):
        self.score += points 
        print(f"Player's score: {self.score}")

    def jump(self):
        self.y_velo = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def move_left(self, velo):
        self.x_velo = -velo
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, velo):
        self.x_velo = velo
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_velo += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_velo, self.y_velo)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_velo = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_velo = 0

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.x_velo != 0:
            sprite_sheet = "run"
        elif self.y_velo < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_velo > self.GRAVITY * 2:
            sprite_sheet = "fall"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = py.mask.from_surface(self.sprite) # pixel perfect collision

    def draw(self, win, offset_x):
        # py.draw.rect(win, self.COLOR, self.rect)
        # self.sprite = self.SPRITES["idle_" + self.direction][0]
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

# object class
class Object(py.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = py.Rect(x, y, width, height)
        self.image = py.Surface((width, height), py.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

# block class
class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = py.mask.from_surface(self.image)

# fire class
class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = py.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self): 
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = py.mask.from_surface(self.image) # pixel perfect collision

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Arrow(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "arrow")
        self.arrow = load_sprite_sheets("Traps", "Arrow", width, height)
        self.image = self.arrow["idle"][0]
        self.mask = py.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "idle"

    def loop(self):
        sprites = self.arrow[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = py.mask.from_surface(self.image) # pixel perfect collision

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


class RedMushroom(Object):
    ANIMATION_DELAY = 10
    VELOCITY = 2

    def __init__(self, x, y, width, height, objects):
        super().__init__(x, y, width, height, "red_mushroom")
        self.ent = load_sprite_sheets("Enemies", "RedMushroom", width, height)
        self.image = self.ent["RedMushroom"][0]
        self.mask = py.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "RedMushroom"
        self.velocity_x = self.VELOCITY
        self.objects = objects
        self.active = True  # to indicate mushroom's state

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def loop(self):
        # Animation and movement logic as before
        if not self.active:
            return

        sprites = self.ent[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        # Horizontal collision and direction reversal
        if self.velocity_x < 0:
            collide_left = collide(self, self.objects, -abs(self.velocity_x))
            if collide_left:
                self.velocity_x = abs(self.velocity_x)
        else:
            collide_right = collide(self, self.objects, abs(self.velocity_x))
            if collide_right:
                self.velocity_x = -abs(self.velocity_x)

        # Move the mushroom horizontally
        self.rect.x += self.velocity_x
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = py.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

    def handle_player_collision(self, player):
        # Check if player hits the mushroom from above
        vertical_collide = handle_vertical_collision(player, [self], player.y_velo)
        if vertical_collide:
            # Deactivate the mushroom
            self.active = False
            print("Mushroom was hit from above and deactivated.")
            return "mushroom_hit"

        # Check for horizontal collision
        if py.sprite.collide_mask(player, self):
            player.active = False  # Deactivate player (they "die")
            print("Player collided horizontally with mushroom and deactivated.")
            return "player_hit"

        return None

def handle_collisions(player, mushrooms):
    for mushroom in mushrooms:
        if mushroom.active:  # Only check active mushrooms
            collision_result = mushroom.handle_player_collision(player)
            if collision_result == "mushroom_hit":
                print("Mushroom was hit and removed.")
                # Code to remove mushroom from the game, if needed
            elif collision_result == "player_hit":
                print("Player collided with mushroom and died.")
                # Code to handle player's death, like resetting the level

# coin class
class Coin(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "coin")
        self.coin = load_sprite_sheets("Items", "Coins", width, height)
        self.image = self.coin["idle"][0]
        self.mask = py.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "idle"
        self.appear = False
        self.active = True

    def idle(self):
        self.animation_name = "idle"

    def spin(self):
        self.animation_name = "spin"
    
    def loop(self):
        sprites = self.coin[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = py.mask.from_surface(self.image) # pixel perfect collision

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

    def remove(self):
        # self.active = False
        self.rect = py.Rect(-100, -100, 0, 0)

    def draw(self, win, offset_x):
        if self.active:
            win.blit(self.image, (self.rect.x - offset_x, self.rect.y))
            self.spin()

# mystery box class
class MysteryBox(Object):
    ANIMATION_DELAY = 10
    def __init__(self, x, y, width, height, name=None):
        super().__init__(x, y, width, height, "coinbox")
        self.box = load_sprite_sheets("Items", "Coinbox", width, height)
        self.image = self.box["coinbox"][0]
        self.mask = py.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "coinbox"
        self.active = True
        self.coin = None

    def get_hit(self, player):
        if self.active:
            self.active = False
            # self.animation_name = "hit"
            player.increase_score(1)
            # coin appears where the box was hit
            self.coin = Coin(self.rect.x, self.rect.y - 20, 16, 16)
            return self.coin

    def loop(self):
        sprites = self.box[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = py.mask.from_surface(self.image) # pixel perfect collision

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

        if self.coin and self.coin.active:
            self.coin.loop()
        elif self.coin and not self.coin.active:
            self.coin = None 

        # if the box is hit
        if not self.active:
            self.image = self.box["coinbox"][0]
            self.mask = py.mask.from_surface(self.image)


def get_background(bg_name):
    image = py.image.load(join("assets", "Background", bg_name))
    _, _, width, height = image.get_rect()
    tiles = []

    for x in range(WIDTH // width + 1):
        for y in range(HEIGHT // height + 1):
            pos = [x * width, y * height]
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tuple(tile))

    for obj in objects:
        if isinstance(obj, Coin) and not obj.active:
            continue
        obj.draw(window, offset_x)

    player.draw(window, offset_x)
    py.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if py.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
                if obj.name == "coinbox":
                    obj.get_hit(player)

            collided_objects.append(obj)

    return collided_objects

# check for collision and move player to the edge of the object
def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collide_object = None
    for obj in objects:
        if py.sprite.collide_mask(player, obj):
            collide_object = obj
            break
    player.move(-dx, 0)
    player.update()
    return collide_object

def handle_movement(player, objects, coins):
    keys = py.key.get_pressed()

    player.x_velo = 0
    collide_left = collide(player, objects, -PLAYER_VELO * 2)
    collide_right = collide(player, objects, PLAYER_VELO * 2)

    if keys[py.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VELO)
    if keys[py.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VELO)

    vertical_collide = handle_vertical_collision(player, objects, player.y_velo)
    to_check = [collide_left, collide_right, *vertical_collide]
    
    for obj in to_check:
        if obj and (obj.name == "fire" or obj.name == "red_mushroom"):
            player.make_hit()
    
    # Check for collisions with coins
    for coin in coins:
        if player.rect.colliderect(coin.rect) and coin.active:  # check if coin is active
            player.increase_score(1)
            coin.remove()  # remove coin

# main loop
def main(window):
    clock = py.time.Clock()
    block_size = 96
    background, bg_image = get_background("Blue.png")
    player = Player(100, 100, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    arrow = Arrow(200, HEIGHT - block_size - 64, 18, 18)
    red_mushroom = RedMushroom(500, HEIGHT - block_size - 36, 20, 22, [Block(block_size * 4, HEIGHT - block_size * 2, block_size), Block(block_size * 8, HEIGHT - block_size * 2, block_size)])
    coins = [Coin(random.randint(0, WIDTH), HEIGHT - block_size - 64, 16, 16) for _ in range(5)]
    coinbox = MysteryBox(300, HEIGHT - block_size - 124, 16, 16)
    # koopa = Koopa.Koopa(500, HEIGHT - block_size - 36, 20, 22, [Block(block_size * 4, HEIGHT - block_size * 2, block_size), Block(block_size * 8, HEIGHT - block_size * 2, block_size)], None)
    
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]
    objects = [*floor, fire, *coins, arrow, red_mushroom, coinbox, 
                Block(0, HEIGHT - block_size * 2, block_size),
                Block(block_size * 4, HEIGHT - block_size * 2, block_size),
                Block(block_size * 8, HEIGHT - block_size * 2, block_size),
                Block(block_size * 3, HEIGHT - block_size * 4, block_size),]

    offset_x = 0
    scroll_area_width = WIDTH // 4

    run = True
    while run:
        clock.tick(FPS)
        for event in py.event.get():
            if event.type == py.QUIT:
                run = False
                break
            if event.type == py.KEYDOWN:
                if (event.key == py.K_UP or event.key == py.K_SPACE) and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        fire.loop()
        arrow.loop()
        red_mushroom.loop()
        coinbox.loop()
        for coin in coins:
            coin.loop()

        handle_movement(player, objects, coins)  # Pass coins to the movement handler
        handle_collisions(player, [red_mushroom])
        draw(window, background, bg_image, player, objects, offset_x)

        if (player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_velo > 0) or (
            player.rect.left - offset_x <= scroll_area_width and player.x_velo < 0):
            offset_x += player.x_velo

    py.quit()
    quit()
    

if __name__ == "__main__":
    main(window)
