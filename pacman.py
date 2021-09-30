from road import *
from ghost import *
from sprites import PacmanSprite
from pygame.locals import *
from vector import Vector
from constants import *
import pygame


class Pacman(object):
    def __init__(self, road_block, road_blocks):
        self.position = None
        self.name = PACMAN
        self.position = None
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
        self.goal_finder = GoalFinder(road_blocks)
        self.goal_road = []

    def set_position(self):
        self.position = self.road_block.position.copy()

    def find_block_direction(self):
        for key, value in self.road_block.directions.items():
            if value == self.target_block:
                return key
        return STOP

    def update(self, dt):
        if len(self.goal_road) == 0:
            self.goal_road = self.goal_finder.get_goal_road(self.road_block)
            self.goal_finder.visit_block(self.road_block)
            self.target_block = self.goal_road.pop(0)
            self.direction = self.find_block_direction()
            self.set_position()

        self.sprite.update(dt)

        self.position += self.directions[self.direction] * self.speed * dt

        if isinstance(self.target_block, PortalBlock) and isinstance(self.road_block, PortalBlock):
            self.road_block = self.target_block
            self.goal_finder.visit_block(self.road_block)
            self.set_position()

        if self.is_exceeded_the_boundaries():
            self.road_block = self.target_block
            self.goal_finder.visit_block(self.road_block)
            self.set_position()
            if not len(self.goal_road) == 0:
                self.target_block = self.goal_road.pop(0)
                self.direction = self.find_block_direction()
                self.set_position()
            if len(self.goal_road) == 0:
                self.goal_road = self.goal_finder.get_goal_road(self.target_block)
                if not self.goal_road:
                    self.goal_road = [self.target_block]

    def player_update(self, dt):
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
        self.goal_road = []


def heuristic(a, b):
    return abs(a.position.x - b.position.x) + abs(a.position.y - b.position.y)


class GoalFinder(object):
    def __init__(self, road_blocks):
        self.road_blocks = road_blocks
        self.visited = []
        self.graph = {}
        self.create_weighted_graph()

    def visit_block(self, road_block):
        if road_block not in self.visited:
            self.visited.append(road_block)

    def create_weighted_graph(self):
        for item in self.road_blocks:
            if not isinstance(item, NullRoad) and not isinstance(item, GhostBlock):
                self.graph[item] = {}
                for direction in item.directions.values():
                    if not isinstance(direction, NullRoad) and not isinstance(direction, GhostBlock):
                        if isinstance(item, PortalBlock) and isinstance(direction, PortalBlock):
                            self.graph[item][direction] = 0
                        else:
                            self.graph[item][direction] = \
                                (item.position - direction.position).magnitude_squared()

    def get_random_goal(self):
        while True:
            block = random.choice(list(self.graph.keys()))
            if block not in self.visited:
                return block

    def get_goal_road(self, start):
        goal = self.get_random_goal()
        path = self.a_star(start, goal)
        path = self.get_road(path, start, goal)
        return path

    def a_star(self, start, goal):
        queue = [(0, start)]
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while queue:
            queue = sorted(queue, key=lambda x: x[0])
            (priority, vertex) = queue.pop(0)

            if vertex == goal:
                return came_from

            for next in self.graph[vertex].keys():
                new_cost = cost_so_far[vertex] + self.graph[vertex][next]
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    queue.append((priority, next))
                    came_from[next] = vertex

    def get_road(self, path, start, goal):
        road = []
        current = goal
        while current != start:
            road.append(current)
            current = path[current]
        road.reverse()
        return road
