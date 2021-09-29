from road import *
import random
import pygame
from constants import *


class Sprite(object):
    def __init__(self, name, tile_width, tile_height):
        self.sheet = pygame.image.load(name).convert()
        transcolor = self.sheet.get_at((0, 0))
        self.sheet.set_colorkey(transcolor)
        width = int(self.sheet.get_width() / tile_width * TILEWIDTH)
        height = int(self.sheet.get_height() / tile_height * TILEHEIGHT)
        self.sheet = pygame.transform.scale(self.sheet, (width, height))

    def get_image(self, x, y, width, height):
        x *= TILEWIDTH
        y *= TILEHEIGHT
        self.sheet.set_clip(pygame.Rect(x, y, width, height))
        return self.sheet.subsurface(self.sheet.get_clip())


class MazeSprites(object):
    def __init__(self, game_map):
        self.sheet = pygame.image.load("Mazeparts2.png").convert()
        width = int(self.sheet.get_width() / 25 * TILEWIDTH)
        height = int(self.sheet.get_height() / 25 * TILEHEIGHT)
        self.sheet = pygame.transform.scale(self.sheet, (width, height))
        self.map = game_map

    def get_image(self, x, y):
        x *= TILEWIDTH
        y *= TILEHEIGHT
        self.sheet.set_clip(pygame.Rect(x, y, TILEWIDTH, TILEWIDTH))
        return self.sheet.subsurface(self.sheet.get_clip())

    def make_background(self, background):
        for row in range(len(self.map.map)):
            for col in range(len(self.map.map[row])):
                if self.map.map[row][col] >= 50 or self.map.map[row][col] == 0:
                    x = random.randint(0, 11)
                    sprite = self.get_image(x, 0)
                    background.blit(sprite, (col * TILEHEIGHT, row * TILEWIDTH))
                elif self.map.map[row][col] == 13:
                    x = 15
                    sprite = self.get_image(x, 0)
                    background.blit(sprite, (col * TILEHEIGHT, row * TILEWIDTH))
                elif self.map.map[row][col] == 15:
                    x = 13
                    sprite = self.get_image(x, 0)
                    background.blit(sprite, (col * TILEHEIGHT, row * TILEWIDTH))
                elif self.map.map[row][col] in [16, 17, 18, 19, 22]:
                    x = 14
                    sprite = self.get_image(x, 0)
                    background.blit(sprite, (col * TILEHEIGHT, row * TILEWIDTH))
                else:
                    x = 12
                    sprite = self.get_image(x, 0)
                    background.blit(sprite, (col * TILEHEIGHT, row * TILEWIDTH))

        return background


class PacmanSprite(Sprite):
    def __init__(self, pacman):
        Sprite.__init__(self, "pacman.png", 32, 32)
        self.pacman = pacman
        self.sprites = {}
        self.get_sprites()
        self.pacman.image = self.get_start_image()

    def get_start_image(self):
        return self.get_image(1, 0)

    def get_image(self, x, y):
        return Sprite.get_image(self, x, y, TILEWIDTH, TILEHEIGHT)

    def get_sprites(self):
        self.sprites[LEFT] = Sprites(((1, 0), (1, 1)))  # (1, 0), (1, 1)
        self.sprites[RIGHT] = Sprites(((1, 2), (1, 3)))  # ((2, 1), (3, 1)))
        self.sprites[UP] = Sprites(((0, 0), (0, 1)))  # ((0, 0), (0, 1)))
        self.sprites[DOWN] = Sprites(((0, 2), (0, 3)))  # ((0, 2), (0, 3)))

    def update(self, dt):
        if self.pacman.direction == LEFT:
            self.pacman.image = self.get_image(*self.sprites[LEFT].update(dt))
        elif self.pacman.direction == RIGHT:
            self.pacman.image = self.get_image(*self.sprites[RIGHT].update(dt))
        elif self.pacman.direction == DOWN:
            self.pacman.image = self.get_image(*self.sprites[DOWN].update(dt))
        elif self.pacman.direction == UP:
            self.pacman.image = self.get_image(*self.sprites[UP].update(dt))


class GhostSprite(Sprite):
    def __init__(self, ghost, sprite_name):
        Sprite.__init__(self, sprite_name, 32, 32)
        self.ghost = ghost
        self.sprites = {}
        self.get_sprites()
        self.ghost.image = self.get_start_image()

    def get_start_image(self):
        return self.get_image(1, 0)

    def get_image(self, x, y):
        return Sprite.get_image(self, x, y, TILEWIDTH, TILEHEIGHT)

    def get_sprites(self):
        self.sprites[LEFT] = Sprites(((1, 0), (1, 1)))  # (1, 0), (1, 1)
        self.sprites[RIGHT] = Sprites(((1, 2), (1, 3)))  # ((2, 1), (3, 1)))
        self.sprites[UP] = Sprites(((0, 0), (0, 1)))  # ((0, 0), (0, 1)))
        self.sprites[DOWN] = Sprites(((0, 2), (0, 3)))  # ((0, 2), (0, 3)))

    def update(self, dt):
        if self.ghost.direction == LEFT:
            self.ghost.image = self.get_image(*self.sprites[LEFT].update(dt))
        elif self.ghost.direction == RIGHT:
            self.ghost.image = self.get_image(*self.sprites[RIGHT].update(dt))
        elif self.ghost.direction == DOWN:
            self.ghost.image = self.get_image(*self.sprites[DOWN].update(dt))
        elif self.ghost.direction == UP:
            self.ghost.image = self.get_image(*self.sprites[UP].update(dt))


class FruitSprite(Sprite):
    def __init__(self, fruit):
        Sprite.__init__(self, "cherry-2d.png", 250, 250)
        self.fruit = fruit
        self.fruit.image = self.get_start_image()

    def get_start_image(self):
        return self.get_image(0, 0)

    def get_image(self, x, y):
        return Sprite.get_image(self, x, y, TILEWIDTH, TILEHEIGHT)


class CoinSprite(Sprite):
    def __init__(self, point, name):
        Sprite.__init__(self, name, 32, 32)
        self.point = point
        self.point.image = self.get_start_image()

    def get_start_image(self):
        return self.get_image(0, 0)

    def get_image(self, x, y):
        return Sprite.get_image(self, x, y, TILEWIDTH, TILEHEIGHT)


class Sprites(object):
    def __init__(self, frames):
        self.frames = frames
        self.current_frame = 0
        self.speed = FRAMESPEED
        self.dt = 0

    def update(self, dt):
        self.next_frame(dt)
        if self.current_frame == len(self.frames):
            self.current_frame = 0
        return self.frames[self.current_frame]

    def next_frame(self, dt):
        self.dt += dt
        if self.dt >= (1.0 / self.speed):
            self.current_frame += 1
            self.dt = 0
