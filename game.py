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


class GameController(object):
    def __init__(self):
        pygame.init()
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
        pygame.display.set_caption(GAMENAME)
        self.ghosts_finder = None

    def set_background(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def start_game(self):
        self.set_background()
        self.road = Map()
        self.maze_sprites = MazeSprites(self.road)
        self.background = self.maze_sprites.make_background(self.background)
        self.points = Points(self.road)
        self.points_start_number = len(self.points.points)
        self.ghosts = Ghosts(self.road)
        self.pacman = Pacman(self.road.get_spawn_position(), self.road.road_blocks)
        self.texts = Texts()
        self.texts.update_level(self.level)
        self.texts.update_score(self.score)
        self.texts.update_lives(self.lives)
        self.texts.hide_text(KILLTHEMTXT)
        self.texts.hide_text(WINTXT)
        self.ghosts_finder = GhostFinder(self.road.road_blocks, self.pacman, self.ghosts)

    def update(self):
        if self.lives != 0:
            dt = self.clock.tick(30) / 1000.0
            self.pacman.update(dt)
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
        self.start_game()

    def end_game(self):
        self.texts.show_text(WINTXT)
        self.lives = 0

    def check_death(self):
        self.ghosts.respawn()
        self.pacman.respawn()
        self.lives -= 1
        self.texts.update_lives(self.lives)
        if self.lives == 0:
            self.game_over()

    def game_over(self):
        self.texts.show_text(GAMEOVERTXT)
        self.texts.texts[GAMEOVERTXT].render(self.screen)

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
            self.lives = 3
            self.score = 0
            self.level = 1
            self.start_game()
        if key_pressed[K_z]:
            self.ghosts_finder.change_algorithm()
            self.texts.update_algorithm(self.ghosts_finder.current)
            self.clock.tick(20)
        if key_pressed[K_x]:
            self.texts.update_time(self.ghosts_finder.timer.elapsed)
            self.pacman.goal_finder.get_goal_road(self.pacman.road_block)
            self.clock.tick(20)

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
