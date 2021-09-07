import pygame
from pygame.locals import *
from vector import Vector
from constants import *
from road import *
from ghost import *
from sprites import PacmanSprite


class Pacman(object):
    def __init__(self, road_block):
        self.position = None
        self.name = PACMAN
        self.positon = None
        self.directions = {STOP: Vector(), UP: Vector(0, -1), DOWN: Vector(0, 1), LEFT: Vector(-1, 0),
                           RIGHT: Vector(1, 0)}
        self.direction = STOP
        self.speed = 100
        self.radius = 10
        self.color = YELLOW
        self.road_block = road_block
        self.target_block = road_block
        self.spawn_block = road_block
        self.set_position()
        self.image = None
        self.sprite = PacmanSprite(self)

    def set_position(self):
        self.position = self.road_block.position.copy()

    def update(self, dt):
        self.sprite.update(dt)
        direction = self.get_valid_key
        self.position += self.directions[self.direction] * self.speed * dt
        if isinstance(self.target_block, PortalBlock) and isinstance(self.road_block, PortalBlock):
            self.road_block = self.target_block
            self.set_position()

        if self.is_exceeded_the_boundaries():
            self.road_block = self.target_block
            self.target_block = self.get_new_target_block(direction)
            if self.target_block is self.road_block:
                self.target_block = self.get_new_target_block(direction)
            else:
                self.direction = direction
            if self.target_block is self.road_block:
                self.direction = STOP
            self.set_position()
        else:
            if self.is_direction_opposite(direction):
                self.change_direction()

    def is_valid_direction(self, direction):
        if direction is not STOP:
            if not isinstance(self.road_block.directions[direction], NullRoad) and not \
                    isinstance(self.road_block.directions[direction], GhostBlock):
                return True
        return False

    def get_new_target_block(self, direction):
        if self.is_valid_direction(direction):
            return self.road_block.directions[direction]
        return self.road_block

    def is_exceeded_the_boundaries(self):
        if self.target_block is not None:
            vector_1 = self.target_block.position - self.road_block.position
            vector_2 = self.position - self.road_block.position
            blocks_space = vector_1.magnitude_squared()
            passed = vector_2.magnitude_squared()
            return passed >= blocks_space
        return False

    def change_direction(self):
        self.direction *= -1
        temp = self.road_block
        self.road_block = self.target_block
        self.target_block = temp

    def is_direction_opposite(self, direction):
        if direction is not STOP:
            if direction == self.direction * -1:
                return True
        return False

    def get_point(self, points):
        for point in points:
            if self.is_touching(point):
                return point
        return None

    def get_ghost(self, ghosts):
        for ghost in ghosts:
            if self.is_touching(ghost):
                return ghost
        return None

    def is_touching(self, other):
        distance = self.position - other.position
        distance = distance.magnitude_squared()
        radius_distance = (other.radius + self.radius) ** 2
        if distance <= radius_distance:
            return True
        return False

    @property
    def get_valid_key(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP

    def render(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.position.as_tuple())
        else:
            position = self.position.as_int()
            pygame.draw.circle(screen, self.color, position, self.radius)

    def respawn(self):
        self.road_block = self.target_block = self.spawn_block


