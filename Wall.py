import pygame


class Wall:
    def __init__(self, parent_screen):
        self.wall = pygame.image.load("resources/wall.jpg").convert()
        self.parent_screen = parent_screen
        self.x = 0
        self.y = 0

    def draw(self, xy):  # (x, y) packed as a tuple
        self.parent_screen.blit(self.wall, xy)  # draw wall block image
