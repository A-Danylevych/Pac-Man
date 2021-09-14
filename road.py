from points import *
from vector import *
from constants import *
from generator import Generator
import pygame
import numpy as np
import random


class MapPosition(object):

    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __eq__(self, other):
        if self.row == other.row and self.col == other.col:
            return True
        return False

    def as_vector(self):
        return Vector(self.col * TILEHEIGHT, self.row * TILEWIDTH)


class RoadBlock(object):

    def __init__(self, position):
        self.position = position.as_vector()
        self.map_position = position
        self.directions = {UP: NullRoad(), DOWN: NullRoad(), LEFT: NullRoad(), RIGHT: NullRoad()}

    def render(self, screen):
        for direction in self.directions.keys():
            if not isinstance(self.directions[direction], NullRoad) and not \
                    isinstance(self.directions[direction], PortalBlock) and not \
                    isinstance(self.directions[direction], GhostBlock) and not isinstance(self, GhostBlock):
                start_block = self.position.as_tuple()
                end_block = self.directions[direction].position.as_tuple()
                pygame.draw.line(screen, WHITE, start_block, end_block, 4)
                pygame.draw.circle(screen, RED, self.position.as_int(), 12)

    def connected(self):
        if not isinstance(self.directions[UP], NullRoad) or not isinstance(self.directions[DOWN], NullRoad) or not \
                isinstance(self.directions[RIGHT], NullRoad) or not isinstance(self.directions[LEFT], NullRoad):
            return True
        return False


class NullRoad(RoadBlock):
    def __init__(self):
        self.position = None


class PortalBlock(RoadBlock):
    def __init__(self, position):
        super(PortalBlock, self).__init__(position)


class GhostBlock(RoadBlock):
    def __init__(self, position):
        super(GhostBlock, self).__init__(position)


class Map(object):
    def __init__(self):
        self.map = self.create_map()
        self.road_blocks_tiles = [ROADBLOCKTILE, PORTALTILE, INKYSPAWN, BLINKYSPAWN, PINKYSPAWN, CLYDESPAWN,
                                  PACMANSPAWN, FRUITTILE]
        self.road_blocks = []
        self.null_road_blocks = [NONEROADTILE]
        self.ghosts_tiles = [INKYSPAWN, BLINKYSPAWN, PINKYSPAWN, CLYDESPAWN]
        self.map_load()
        self.connect_roads()
        self.connect_portals()

    @staticmethod
    def is_road_block(maze, row, col):
        road_tiles = [ROADBLOCKTILE, ROADTILE]
        if maze[row][col] == ROADTILE:
            if maze[row+1][col] != NONEROADTILE and maze[row][col+1] != NONEROADTILE:
                return True
            if maze[row-1][col] != NONEROADTILE and maze[row][col-1] != NONEROADTILE:
                return True
            if maze[row+1][col] != NONEROADTILE and maze[row][col-1] != NONEROADTILE:
                return True
            if maze[row-1][col] != NONEROADTILE and maze[row][col + 1] != NONEROADTILE:
                return True
            if maze[row - 1][col] in road_tiles and maze[row + 1][col] in road_tiles:
                return False
            if maze[row][col + 1] in road_tiles and maze[row][col - 1] in road_tiles:
                return False
            return True
        return False

    @staticmethod
    def add_portal(maze, col):
        while True:
            row = random.randint(0, NROWS - 1)
            if maze[row][col] == ROADBLOCKTILE:
                maze[row][col] = PORTALTILE
                return maze

    @staticmethod
    def create_map():

        game_map = np.zeros((NROWS, NCOLS), int)

        generator = Generator()
        generated_map = generator.generate(NROWS-6, NCOLS-2)
        for row in range(3, NROWS-3, 1):
            for col in range(1, NCOLS-1, 1):
                game_map[row][col] = generated_map[row-3][col-1]

        for row in range(NROWS):
            for col in range(NCOLS):
                if Map.is_road_block(game_map, row, col):
                    game_map[row][col] = ROADBLOCKTILE

        game_map = Map.add_portal(game_map, 1)
        game_map = Map.add_portal(game_map, NCOLS-3)

        count = 2
        while count != 0:
            row = random.randint(0, NROWS - 1)
            col = random.randint(0, NCOLS - 1)
            if game_map[row][col] == ROADBLOCKTILE:
                game_map[row][col] = 22 - count
                count -= 1
        count = 8
        while count != 0:
            row = random.randint(0, NROWS - 1)
            col = random.randint(0, NCOLS - 1)
            if game_map[row][col] == ROADTILE:
                game_map[row][col] = BIGPOINTTILE
                count -= 1
        return game_map

    def map_load(self):
        for row in range(len(self.map)):
            for col in range(len(self.map[row])):
                if self.map[row][col] == ROADBLOCKTILE or self.map[row][col] == PACMANSPAWN or\
                        self.map[row][col] == FRUITTILE:
                    map_position = MapPosition(row, col)
                    road_block = RoadBlock(map_position)
                    self.road_blocks.append(road_block)
                elif self.map[row][col] == PORTALTILE:
                    map_position = MapPosition(row, col)
                    road_block = PortalBlock(map_position)
                    self.road_blocks.append(road_block)
                elif self.map[row][col] in self.ghosts_tiles:
                    map_position = MapPosition(row, col)
                    road_block = GhostBlock(map_position)
                    self.road_blocks.append(road_block)

    def connect_roads(self):
        for index in range(len(self.road_blocks)):
            self.road_blocks[index] = self.connect_horizontally(self.road_blocks[index])
            self.road_blocks[index] = self.connect_vertically(self.road_blocks[index])

    def connect_portals(self):
        first, second = self.find_portals_indexes()
        if self.road_blocks[first].map_position.col > self.road_blocks[second].map_position.col:
            self.road_blocks[first].directions[RIGHT] = self.road_blocks[second]
            self.road_blocks[second].directions[LEFT] = self.road_blocks[first]
        else:
            self.road_blocks[first].directions[LEFT] = self.road_blocks[second]
            self.road_blocks[second].directions[RIGHT] = self.road_blocks[first]

    def find_portals_indexes(self):
        for index in range(len(self.road_blocks)):
            if isinstance(self.road_blocks[index], PortalBlock):
                second_index = self.find_pair(index)
                return index, second_index

    def find_pair(self, first_index):
        for index in range(first_index + 1, len(self.road_blocks)):
            if isinstance(self.road_blocks[index], PortalBlock):
                return index

    def connect_vertically(self, road_block):
        col, row = self.position_to_col_row(road_block)
        for index in range(row - 1, -1, -1):
            if self.map[index][col] in self.null_road_blocks:
                break
            if self.map[index][col] in self.road_blocks_tiles:
                road_block.directions[UP] = self.filter(index, col)
                break
        for index in range(row + 1, len(self.map)):
            if self.map[index][col] in self.null_road_blocks:
                break
            if self.map[index][col] in self.road_blocks_tiles:
                road_block.directions[DOWN] = self.filter(index, col)
                break
        return road_block

    def filter(self, row, col):
        for block in self.road_blocks:
            if block.map_position == MapPosition(row, col):
                return block

    def connect_horizontally(self, road_block):
        col, row = self.position_to_col_row(road_block)
        for index in range(col - 1, -1, -1):
            if self.map[row][index] in self.null_road_blocks:
                break
            if self.map[row][index] in self.road_blocks_tiles:
                road_block.directions[LEFT] = self.filter(row, index)
                break
        for index in range(col + 1, len(self.map[row])):
            if self.map[row][index] in self.null_road_blocks:
                break
            if self.map[row][index] in self.road_blocks_tiles:
                road_block.directions[RIGHT] = self.filter(row, index)
                break
        return road_block

    @staticmethod
    def position_to_col_row(road_block):
        return road_block.map_position.col, road_block.map_position.row

    def render(self, screen):
        for road_block in self.road_blocks:
            road_block.render(screen)

    def ghosts_positions(self):
        ghosts = {}
        for row in range(len(self.map)):
            for col in range(len(self.map[row])):
                if self.map[row][col] == INKYSPAWN:
                    ghosts[INKY] = self.filter(row, col)
                elif self.map[row][col] == BLINKYSPAWN:
                    ghosts[BLINLY] = self.filter(row, col)
                elif self.map[row][col] == PINKYSPAWN:
                    ghosts[PINKY] = self.filter(row, col)
                elif self.map[row][col] == CLYDESPAWN:
                    ghosts[CLYDE] = self.filter(row, col)
        return ghosts

    def get_spawn_position(self):
        for row in range(len(self.map)):
            for col in range(len(self.map[row])):
                if self.map[row][col] == PACMANSPAWN:
                    return self.filter(row, col)

    def create_points_list(self):
        points = []
        big_points = []
        for row in range(len(self.map)):
            for col in range(len(self.map[row])):
                if self.map[row][col] in [ROADTILE, ROADBLOCKTILE]:
                    points.append(Point(MapPosition(row, col), "silver.png"))
                elif self.map[row][col] == BIGPOINTTILE:
                    big_point = BigPoint(MapPosition(row, col), "gold.png")
                    points.append(big_point)
                    big_points.append(big_point)
        return points, big_points

    def get_fruit_position(self):
        for row in range(len(self.map)):
            for col in range(len(self.map[row])):
                if self.map[row][col] == FRUITTILE:
                    return MapPosition(row, col)
