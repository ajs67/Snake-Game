import pygame
import random as r


class Food:
    def __init__(self, parent_screen, block_size):
        self.image = pygame.image.load(self.image_file).convert()
        self.parent_screen = parent_screen
        self.block_size = block_size
        self.x = -1*40
        self.y = -1*40

    @property
    def image_file(self):
        raise NotImplementedError

    def move(self):
        self.x = r.randint(1, 23) * self.block_size
        self.y = r.randint(1, 18) * self.block_size

    def draw(self):
        self.parent_screen.blit(self.image, (self.x + 1, self.y + 1))  # pos + 1 to position, so it doesn't cover grid

    def remove(self):  # place the food outside the game board
        self.x = -1 * self.block_size
        self.y = -1 * self.block_size


class Apple(Food):
    image_file = "resources/apple.jpg"


class Star(Food):
    image_file = "resources/star.jpg"
