import numpy as np
from constants import *
import random


def get_random(array):
    return random.choice(array)


def is_even(n):
    return n % 2 == 0


def is_maze(maze, nrows, ncols):
    for x in range(ncols):
        for y in range(nrows):
            if is_even(x) and is_even(y) and maze[y][x] == NONEROADTILE:
                return False
    return True


def has_neibors(maze, row, col, nrows, ncols):
    if row+1 < nrows and maze[row+1][col] != NONEROADTILE:
        return True
    if row-1 > 0 and maze[row-1][col] != NONEROADTILE:
        return True
    if col+1 < ncols and maze[row][col+1] != NONEROADTILE:
        return True
    if col-1 > 0 and maze[row][col-1] != NONEROADTILE:
        return True
    return False

class Generator(object):
    @staticmethod
    def generate(nrows, ncols):
        game_map = np.zeros((nrows, ncols), int)
        x_arr = np.zeros(ncols, int)
        y_arr = np.zeros(nrows, int)
        filter_x = []
        filter_y = []
        for index in range(len(x_arr)):
            if is_even(index):
                filter_x.append(index)
        for index in range(len(y_arr)):
            if is_even(index):
                filter_y.append(index)
        start_x = get_random(filter_x)
        start_y = get_random(filter_y)

        pathfinder = PathFinder(start_x, start_y)
        game_map[start_y][start_x] = ROADTILE
        while not is_maze(game_map, nrows, ncols):
            game_map = pathfinder.move(game_map, nrows, ncols)

        count = 4
        while count != 0:
            row = random.randint(0, nrows-1)
            col = random.randint(0, ncols-1)
            if game_map[row][col] == NONEROADTILE and has_neibors(game_map, row, col, nrows, ncols):
                game_map[row][col] = 20 - count
                count -= 1

        return game_map


class PathFinder(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, maze, nrows, ncols):
        directions = []
        if self.x > 0:
            directions.append(LEFT)
        if self.x < ncols - 2:
            directions.append(RIGHT)
        if self.y > 0:
            directions.append(UP)
        if self.y < nrows - 2:
            directions.append(DOWN)

        direction = get_random(directions)

        if direction == LEFT:
            if maze[self.y][self.x-2] == NONEROADTILE:
                maze[self.y][self.x-1] = ROADTILE
                maze[self.y][self.x - 2] = ROADTILE
            self.x -= 2
        elif direction == RIGHT:
            if maze[self.y][self.x+2] == NONEROADTILE:
                maze[self.y][self.x+1] = ROADTILE
                maze[self.y][self.x+2] = ROADTILE
            self.x += 2
        elif direction == UP:
            if maze[self.y-2][self.x] == NONEROADTILE:
                maze[self.y-1][self.x] = ROADTILE
                maze[self.y-2][self.x] = ROADTILE
            self.y -= 2
        elif direction == DOWN:
            if maze[self.y+2][self.x] == NONEROADTILE:
                maze[self.y+1][self.x] = ROADTILE
                maze[self.y+2][self.x] = ROADTILE
            self.y += 2

        return maze
