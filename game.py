import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from road import *
from maps import *
from points import *
from ghost import *
from fruit import Fruit
from text import Texts
from sprites import *
from ghostfinder import *
import csv
from timer import Timer


class GameController(object):

    @staticmethod
    def get_state():
        return pygame.surfarray.array3d(pygame.display.get_surface())

    def play_step(self, input_actions):
        if sum(input_actions) != 1:
            raise ValueError('Multiple input actions!')

        if input_actions[0] == 1:
            direction = LEFT
        if input_actions[1] == 1:
            direction = UP
        if input_actions[2] == 1:
            direction = RIGHT
        if input_actions[3] == 1:
            direction = DOWN

        cur_score = self.score
        cur_lives = self.lives
        self.update(direction)

        # check for score
        reward = 0
        if cur_score < self.score:
            reward = 1
        if cur_lives > self.lives:
            reward = -1

        return reward, self.game_over, self.score

    def __init__(self):
        pygame.init()
        self.algo = EXPECTIMAX
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.clock = pygame.time.Clock()
        self.background = None
        self.pacman = None
        self.road = None
        self.points = None
        self.ghosts = None
        self.fruit = None
        self.points_start_number = 0
        self.level = 1
        self.score = 0
        self.texts = None
        self.maze_sprites = None
        self.lives = 3
        self.timer = Timer()
        pygame.display.set_caption(GAMENAME)
        self.ghosts_finder = None
        self.game_over = False

    def set_background(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def start_game(self):
        self.game_over = False
        self.set_background()
        self.road = Map()
        self.maze_sprites = MazeSprites(self.road)
        self.background = self.maze_sprites.make_background(self.background)
        self.points = Points(self.road)
        self.points_start_number = len(self.points.points)
        self.ghosts = Ghosts(self.road, 4, 0)
        self.pacman = Pacman(self.road.get_spawn_position(), self.road.road_blocks, self.ghosts, self.points.points,
                             self.algo)
        self.texts = Texts()
        self.texts.update_level(self.level)
        self.texts.update_score(self.score)
        self.texts.update_lives(self.lives)
        self.texts.hide_text(KILLTHEMTXT)
        self.texts.hide_text(WINTXT)
        self.ghosts_finder = GhostFinder(self.road.road_blocks, self.pacman, self.ghosts)
        self.timer.start_seconds()

    def update(self, direction):
        if self.lives != 0:
            dt = self.clock.tick(30) / 1000.0
            self.pacman.player_update(dt, direction)
            self.ghosts.update(dt)
            if self.fruit is not None:
                self.fruit.update(dt)
            self.texts.update(dt)
            self.ghosts_finder.update()
            self.check_points()
            self.check_ghosts()
            self.check_fruit()
            self.check_events()
            self.render()
        else:
            self.check_events()

    def check_points(self):
        point = self.pacman.get_point(self.points.points)
        if point:
            self.points.count += 1
            self.points.points.remove(point)
            self.update_score(point.points)
            if point.name == BIGPOINT:
                self.ghosts.weak_mode()
                self.texts.show_text(KILLTHEMTXT)
        if len(self.points.points) == 0:
            self.level += 1
            self.change_level()

    def update_score(self, points):
        self.score += points
        self.texts.update_score(self.score)

    def change_level(self):
        if self.level == 5:
            self.end_game()
        self.texts.update_level(self.level)
        self.write_statistics(True)
        self.start_game()

    def end_game(self):
        self.texts.show_text(WINTXT)
        self.game_over = True

    def check_death(self):
        self.ghosts.respawn()
        self.pacman.respawn()
        self.lives -= 1
        self.texts.update_lives(self.lives)
        if self.lives == 0:
            self.loosing()

    def loosing(self):
        self.texts.show_text(GAMEOVERTXT)
        self.texts.texts[GAMEOVERTXT].render(self.screen)
        self.write_statistics(False)
        self.game_over = True

    def check_ghosts(self):
        ghost = self.pacman.get_ghost(self.ghosts.ghosts.values())
        if ghost:
            if ghost.mode == WEAK:
                self.update_score(ghost.points)
                ghost.dead_mode()
                for ghost in self.ghosts.ghosts.values():
                    if ghost.mode == WEAK:
                        ghost.points *= 2
            else:
                self.check_death()

    def check_fruit(self):
        if self.points.count * 2 == self.points_start_number:
            self.fruit = Fruit(self.road.get_fruit_position())
            self.update_score(self.fruit.points)
        if self.fruit is not None:
            if self.pacman.is_touching(self.fruit):
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None

    def check_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_SPACE]:
            self.write_statistics(False)
            self.restart()
        if key_pressed[K_z]:
            self.ghosts_finder.change_algorithm()
            self.texts.update_algorithm(self.ghosts_finder.current)
            self.clock.tick(20)
        if key_pressed[K_x]:
            self.texts.update_time(self.ghosts_finder.timer.elapsed)
            self.clock.tick(20)

    def restart(self):
        self.lives = 3
        self.score = 0
        self.level = 1
        self.start_game()

    def render(self):
        self.screen.blit(self.background, (0, 0))
        self.pacman.render(self.screen)
        self.points.render(self.screen)
        self.ghosts.render(self.screen)
        self.texts.render(self.screen)
        self.ghosts_finder.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        pygame.display.update()

    def write_statistics(self, winning):
        self.timer.stop_seconds()
        data = [winning, self.timer.elapsed, self.score, self.algo]

        with open('statistics.csv', 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(data)
