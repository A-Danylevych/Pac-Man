from points import *
from vector import *
from constants import *
import pygame


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
    def __init__(self, game_map):
        self.map = game_map
        self.road_blocks = []
        self.null_road_blocks = [50, NONEROADTILE]
        self.ghosts_tiles = [INKYSPAWN, BLINKYSPAWN, PINKYSPAWN, CLYDESPAWN]
        self.road_blocks_tiles = [ROADBLOCKTILE, PORTALTILE, INKYSPAWN, BLINKYSPAWN, PINKYSPAWN, CLYDESPAWN,
                                  PACMANSPAWN]
        self.road_tiles = [ROADTILE, GHOSTROADTILE]
        self.map_load()
        self.connect_roads()
        self.connect_portals()

    def map_load(self):
        for row in range(len(self.map)):
            for col in range(len(self.map[row])):
                if self.map[row][col] == ROADBLOCKTILE or self.map[row][col] == PACMANSPAWN:
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
        if isinstance(self.road_blocks[first].directions[RIGHT], NullRoad):
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
