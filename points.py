from road import *
from constants import *
import pygame
from sprites import CoinSprite


class Point(object):
    def __init__(self, map_position, name):
        self.name = POINT
        self.position = map_position.as_vector()
        self.color = WHITE
        self.radius = 1/4 * TILEWIDTH
        self.points = 10
        self.image = None
        self.sprite = CoinSprite(self, name)


    def render(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.position.as_tuple())
        else:
            position = self.position.as_int()
            pygame.draw.circle(screen, self.color, position, self.radius)


class BigPoint(Point):
    def __init__(self, map_position, name):
        Point.__init__(self, map_position, name)
        self.name = BIGPOINT
        self.radius = 1/2 * TILEWIDTH
        self.points = 50


class Points(object):
    def __init__(self, game_map):
        self.points, self.big_points = game_map.create_points_list()
        self.count = 0

    def render(self, screen):
        for point in self.points:
            point.render(screen)
