import pygame
from pygame.locals import *
from vector import Vector
from constants import *
from road import *
import random
from sprites import GhostSprite


class Ghost(object):
    def __init__(self, name, road_block, sprite_file, random):
        self.position = None
        self.name = name
        self.positon = None
        self.directions = {STOP: Vector(), UP: Vector(0, -1), DOWN: Vector(0, 1), LEFT: Vector(-1, 0),
                           RIGHT: Vector(1, 0)}
        self.direction = STOP
        self.speed = 100
        self.radius = 10
        self.color = GREEN
        self.road_block = road_block
        self.target_block = road_block
        self.set_position()
        self.points = 200
        self.mode = DEFAULT
        self.timer = 0
        self.mode_time = 30
        self.spawn_block = road_block
        self.image = None
        self.goal = None
        self.sprite = GhostSprite(self, sprite_file)
        self.full_random = random

    def set_position(self):
        self.position = self.road_block.position.copy()

    def update(self, dt):
        self.sprite.update(dt)
        if self.mode == DEAD:
            self.update_mode(dt)
            return

        self.update_mode(dt)
        if self.direction == STOP:
            self.get_direction()
            return
        self.position += self.directions[self.direction] * self.speed * dt

        if isinstance(self.target_block, PortalBlock) and isinstance(self.road_block, PortalBlock):
            self.road_block = self.target_block
            self.set_position()

        if self.is_exceeded_the_boundaries():
            self.road_block = self.target_block
            self.get_direction()
            self.set_position()

    def get_direction(self):
        direction = self.direction_method()
        if self.target_block is self.road_block:
            self.direction = self.direction_method()
        else:
            self.direction = direction

    def direction_method(self):
        if not self.mode == DEFAULT or self.goal is None or len(self.goal) == 0 or self.full_random:
            directions = self.valid_directions()
            direction = self.get_random_direction(directions)
            self.target_block = self.get_new_target_block(direction)
            return direction
        else:
            self.target_block = self.goal.pop(0)
            return self.find_block_direction()

    def find_block_direction(self):
        for key, value in self.road_block.directions.items():
            if value == self.target_block:
                return key
        return STOP

    def update_mode(self, dt):
        self.timer += dt
        if self.timer > self.mode_time and self.mode == DEAD:
            self.mode = DEFAULT
            self.speed = 100
            self.points = 200
        if self.timer > self.mode_time and self.mode == WEAK:
            self.mode = DEFAULT
            self.speed = 100
            self.color = GREEN
            self.points = 200

    @staticmethod
    def get_random_direction(directions):
        return directions[random.randint(0, len(directions) - 1)]

    def is_valid_direction(self, direction):
        if direction is not STOP:
            if not isinstance(self.road_block.directions[direction], NullRoad):
                return True
        return False

    def valid_directions(self):
        directions = []
        for direction in [UP, DOWN, LEFT, RIGHT]:
            if self.is_valid_direction(direction):
                if direction != self.direction * -1:
                    directions.append(direction)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions

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

    def render(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.position.as_tuple())
        else:
            position = self.position.as_int()
            pygame.draw.circle(screen, self.color, position, self.radius)

    def weak_mode(self):
        self.timer = 0
        self.mode = WEAK
        self.speed = 50
        self.color = RED

    def dead_mode(self):
        self.mode = DEAD
        self.timer = 0
        self.respawn()

    def respawn(self):
        self.road_block = self.spawn_block
        self.set_position()
        self.get_direction()


class Ghosts(object):
    def __init__(self, game_map, count, random_count):
        self.ghosts = {}
        self.map = game_map
        self.init_ghosts(count, random_count)

    def render(self, screen):
        for ghost in self.ghosts.values():
            ghost.render(screen)

    def update(self, dt):
        for ghost in self.ghosts.values():
            ghost.update(dt)

    def init_ghosts(self, count, random_count):
        ghosts_tiles = self.map.ghosts_positions()
        k = 0
        random = True
        for ghost_name in ghosts_tiles.keys():
            if k == random_count:
                random = False
            if k == count:
                break
            if ghost_name >= 10:
                self.ghosts[ghost_name] = Ghost(ghost_name, ghosts_tiles[ghost_name], str(4) + ".png", random)
                k += 1
            else:
                self.ghosts[ghost_name] = Ghost(ghost_name, ghosts_tiles[ghost_name], str(ghost_name) + ".png", random)
                k += 1

    def weak_mode(self):
        for ghost in self.ghosts.values():
            ghost.weak_mode()

    def respawn(self):
        for ghost in self.ghosts.values():
            ghost.respawn()

    def get_road_blocks(self):
        blocks = []
        for ghost in self.ghosts.values():
            blocks.append(ghost.road_block)
        return blocks
