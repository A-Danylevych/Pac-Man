import pygame
from constants import *
from sprites import FruitSprite


class Fruit(object):
    def __init__(self, map_position):
        self.name = FRUIT
        self.position = map_position.as_vector()
        self.color = GREEN
        self.lifespan = 500
        self.timer = 0
        self.destroy = False
        self.points = 100
        self.radius = 1/2 * TILEWIDTH
        self.image = None
        self.sprite = FruitSprite(self)

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.lifespan:
            self.destroy = True

    def render(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.position.as_tuple())
        else:
            position = self.position.as_int()
            pygame.draw.circle(screen, self.color, position, self.radius)