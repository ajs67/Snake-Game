import pygame


class Snake:
    # every other block of the snake changes color
    def __init__(self, parent_screen, length, block_size):
        self.odd_block = pygame.image.load("resources/odd_block.jpg").convert()
        self.even_block = pygame.image.load("resources/even_block.jpg").convert()
        self.head_block = pygame.image.load("resources/head_block2.jpg").convert()
        self.tail_block = pygame.image.load("resources/tail_block.jpg").convert()
        self.block_size = block_size
        self.x = [self.block_size * 5] * length
        self.y = [self.block_size * 2] * length
        self.parent_screen = parent_screen
        self.direction = 'right'
        self.length = length

    def increase_length(self):
        self.length += 1
        self.x.append(-1)
        self.y.append(-1)

    def draw(self):
        # snake head
        self.parent_screen.blit(self.head_block, (self.x[0] + 1, self.y[0] + 1))  # x, y + 1 to not cover the grid

        # Blocks alternate colors every other
        for i in range(1, self.length - 1, 2):
            self.parent_screen.blit(self.even_block, (self.x[i], self.y[i]))
        for i in range(2, self.length - 1, 2): # every other block
            self.parent_screen.blit(self.odd_block, (self.x[i], self.y[i]))

        # snake tail
        self.parent_screen.blit(self.tail_block, (self.x[self.length - 1], self.y[self.length - 1]))  # draw tail

    def move_left(self):
        self.direction = 'left'

    def move_right(self):
        self.direction = 'right'

    def move_up(self):
        self.direction = 'up'

    def move_down(self):
        self.direction = 'down'

    def walk(self):

        for i in range(self.length - 1, 0, -1):  # move the position of all blocks to previous block, except head
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]

        #  Move the snake head in the current direction
        if self.direction == 'left':
            self.x[0] -= self.block_size
        elif self.direction == 'right':
            self.x[0] += self.block_size
        elif self.direction == 'down':
            self.y[0] += self.block_size
        elif self.direction == 'up':
            self.y[0] -= self.block_size
        self.draw()
