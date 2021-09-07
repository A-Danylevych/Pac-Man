import pygame
from vector import Vector
from constants import *


class Text(object):
    def __init__(self, text, color, x, y, lifespan=None, id=None, visible=True):
        self.id = id
        self.text = text
        self.lifespan = lifespan
        self.color = color
        self.visible = visible
        self.position = Vector(x, y)
        self.label = None
        self.timer = 0
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.create_label()

    def create_label(self):
        self.label = self.font.render(self.text, True, self.color)

    def set_text(self, text):
        self.text = str(text)
        self.create_label()

    def render(self, screen):
        if self.visible:
            x, y = self.position.as_tuple()
            screen.blit(self.label, (x, y))

    def update(self, dt):
        if self.lifespan is not None and self.visible is True:
            self.timer += dt
            if self.timer >= self.lifespan:
                self.visible = False



class Texts(object):
    def __init__(self):
        self.nextid = 10
        self.texts = {}
        self.setup_text()

    def add_text(self, text, color, x, y, id=None):
        self.nextid += 1
        self.texts[self.nextid] = Text(text, color, x, y, id=id)
        return self.nextid

    def remove_text(self, id):
        self.texts.pop(id)

    def setup_text(self):
        self.texts[SCORETXT] = Text("0".zfill(8), WHITE, 0, TILEHEIGHT)
        self.texts[LEVELTXT] = Text("1".zfill(3), WHITE, 38 * TILEWIDTH, TILEHEIGHT)
        self.texts[GAMEOVERTXT] = Text("GAME OVER!", YELLOW, 15 * TILEWIDTH, 2 * TILEHEIGHT, visible=False)
        self.texts[LIVESTXT] = Text("3".zfill(3), WHITE, 0, 18 * TILEHEIGHT)
        self.texts[KILLTHEMTXT] = Text("KIll Ghosts!!", RED, 15 * TILEWIDTH, TILEHEIGHT, lifespan=30, visible=False)
        self.texts[WINTXT] = Text("YOU WIN!", YELLOW, 15 * TILEWIDTH, 2 * TILEHEIGHT, visible=False)
        self.add_text("LIVES", WHITE, 0, 17 * TILEHEIGHT)
        self.add_text("SCORE", WHITE, 0, 0)
        self.add_text("LEVEL", WHITE, 37 * TILEWIDTH, 0)

    def update(self, dt):
        for text in self.texts.values():
            text.update(dt)

    def hide_text(self, id):
        self.texts[id].visible = False

    def show_text(self, id):
        self.texts[id].visible = True
        self.texts[id].timer = 0

    def update_score(self, score):
        self.update_text(SCORETXT, str(score).zfill(8))

    def update_level(self, level):
        self.update_text(LEVELTXT, str(level).zfill(3))

    def update_lives(self, lives):
        self.update_text(LIVESTXT, str(lives).zfill(3))

    def update_text(self, id, value):
        if id in self.texts.keys():
            self.texts[id].set_text(value)

    def render(self, screen):
        for id in self.texts.keys():
            self.texts[id].render(screen)
