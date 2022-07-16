"""
Snake: Programmed by Alexander Schwartz
Based on the classic nokia snake game, programmed in python

Choose your difficulty:
1 = Slow   2 = Medium   3 = Fast   0 = Impossible
To Play, press Enter or press a number to choose your speed.
To Exit, press Escape

Maps, Images, and the high score save files are all accessed through the resources folder.
"""

# TODO:
# fix snake shape, so it is a clear path from head to tail
# make snake movement smoother
# improve snake block images
# add mouse interface in menu
# add bonus timer snacks worth extra points
# add separate high scores for each map
# separate wall and map objects
# Fix map file transposing when loaded into game (so it can be edited not transposed)
# add 2 player support
# host application online, save a record of high score of all players
# fix game win crash
# develop AI snake that can win the game every time in the shortest amount of time possible
# Implement Multithreading to improve performance. (It seems like game clock slows down randomly)
# Speed and resource optimization


import pygame
from pygame.locals import *
import random as r
import numpy as np
import os
import sys


# block image file is 40 x 40 pixels
BLACK = (0, 0, 0)
WHITE = (255,255,255)
MAX_X = 24
MAX_Y = 19
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
LENGTH_OF_SNAKE = 4
MEDIUM_SPEED = 9


class Wall:
    def __init__(self, parent_screen, block_size):
        self.wall = pygame.image.load("resources/wall.jpg").convert()
        self.parent_screen = parent_screen
        self.block_size = block_size
        self.x = [self.block_size]
        self.y = [self.block_size]
        self.walls = []
        self.map_dict = {
            0: self.blank_map(),
            1: self.equality(),
            2: self.load_map_file("cross.txt"),
            3: self.load_map_file("corners.txt"),
            4: self.load_map_file("crosshair.txt")}

    @staticmethod
    def map_test():
        # test map for debugging
        test_map = np.ones((MAX_X + 1, MAX_Y + 1), dtype=np.uint8)
        test_map[1:-1, 1:MAX_Y // 2 + 2] = 0

        test_map[15:-1, MAX_Y // 2 - 2: MAX_Y // 2 + 2] = 1
        test_map[0:MAX_X, 0:MAX_Y // 3 + 3] = 1
        return test_map

    def blank_map(self):
        map_walls = np.ones((MAX_X+1, MAX_Y+1), dtype=np.uint8)
        map_walls[1:-1, 1:-1] = 0
        return map_walls

    def equality(self):
        map_walls = np.ones((MAX_X+1, MAX_Y+1), dtype=np.uint8)
        map_walls[1:-1, 1:-1] = 0
        map_walls[5:-5, MAX_Y // 3] = 1
        map_walls[5:-5, -MAX_Y // 3] = 1
        return map_walls

    def load_map_file(self,filename):
        file_path = os.path.dirname(__file__) + "/resources/" + filename
        try:
            map_walls = []
            with open(file_path, 'r') as f:
                for line in f.readlines():
                    if len(map_walls) == 0:  # initialize the array with first line
                        values = np.array([int(line, 2)], dtype=np.uint32)  # encode the line into uint32
                        view = values.view(dtype=np.uint8)  # cut the uint 32 into 4 pieces uint8 so unpackbits works

                        # force little endian order so it can decode properly if not already set
                        if values.dtype.byteorder == '>' or (values.dtype.byteorder == '=' and sys.byteorder == 'big'):
                            view = view[::-1]  # reverse the order

                        decoded_line = np.unpackbits(view, count=MAX_Y+1, bitorder='little')[::-1]  # decoded solution
                        map_walls = decoded_line
                    else:  # add each row of the file to the array line by line
                        values = np.array([int(line, 2)], dtype=np.uint32)
                        view = values.view(dtype=np.uint8)

                        decoded_line = np.unpackbits(view, count=MAX_Y + 1, bitorder='little')[::-1]
                        map_walls = np.vstack((map_walls, decoded_line))  # stack each new row at the end of the array
                map_walls = map_walls
                return map_walls
        except IOError:
            print(IOError)
            return self.blank_map()

    def build_map(self, map_blueprint):
        walls_x, walls_y = np.nonzero(map_blueprint)
        walls_y *= self.block_size
        walls_x *= self.block_size
        self.walls = list(zip(walls_x,walls_y))

    def change_map(self, selected_map):
        current_map = self.map_dict.get(selected_map)
        self.build_map(current_map)

    def draw(self):
        for current_pos in self.walls:
            self.parent_screen.blit(self.wall, current_pos)  # draw wall block image


class Apple:
    def __init__(self, parent_screen, block_size):
        self.image = pygame.image.load("resources/apple.jpg").convert()
        self.parent_screen = parent_screen
        self.block_size = block_size
        self.x = 0  # apple starting position x
        self.y = 0  # apple starting position y

    def move(self):
        self.x = r.randint(1, 23) * self.block_size
        self.y = r.randint(1, 18) * self.block_size

    def draw(self):  # draw apple
        self.parent_screen.blit(self.image, (self.x + 1, self.y + 1))  # + 1 to position so it doesn't cover grid


class Snake:
    def __init__(self, parent_screen, length, block_size):
        self.x_block = pygame.image.load("resources/x_block.jpg").convert()
        self.y_block = pygame.image.load("resources/snake_block_2.jpg").convert()
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
        self.parent_screen.blit(self.head_block, (self.x[0] + 1, self.y[0] + 1))  # draw head + 1 to not cover the grid
        for i in range(1, self.length - 1, 2): # every other normal
            if self.direction == 'left' or self.direction == 'right':  # WIP change block image to show shape of snake
                self.parent_screen.blit(self.x_block, (self.x[i], self.y[i]))
            else:
                self.parent_screen.blit(self.x_block, (self.x[i], self.y[i]))
        for i in range(2, self.length - 1, 2): # every other block
            if self.direction == 'left' or self.direction == 'right':
                self.parent_screen.blit(self.y_block, (self.x[i], self.y[i]))
            else:
                self.parent_screen.blit(self.y_block, (self.x[i], self.y[i]))
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

        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]

        if self.direction == 'left':
            self.x[0] -= self.block_size
        elif self.direction == 'right':
            self.x[0] += self.block_size
        elif self.direction == 'down':
            self.y[0] += self.block_size
        elif self.direction == 'up':
            self.y[0] -= self.block_size
        self.draw()


class ScoreBoard:

    def __init__(self, parent_screen, length):
        self.parent_screen = parent_screen
        self.current_score = length
        self.high_score = self.read_high_score()
        self.font = pygame.font.SysFont('arial', 30)  # default font for scores

    def calculate_score(self, length):
        self.current_score = length - LENGTH_OF_SNAKE
        return self.current_score

    def is_new_high_score(self):
        return True if self.high_score < self.current_score else False

    def draw_high_score(self):
        if self.is_new_high_score():
            high_score = self.font.render(f"High Score: {self.current_score}", True, WHITE)
        else:
            high_score = self.font.render(f"High Score: {self.high_score}", True, WHITE)
        self.parent_screen.blit(high_score, (800, 0))

    def draw(self):
        score = self.font.render(f"Score: {self.current_score}", True, WHITE)
        self.parent_screen.blit(score, (600, 0))
        self.draw_high_score()

    def read_high_score(self):
        file_path = os.path.dirname(__file__) + "/resources/high_score.txt"
        try:
            with open(file_path, 'r+') as f:
                score = f.read()
                if not score and score != 0:  # if blank file and score != 0
                    f.write("0")
                    score = 0
                return int(score)
        except IOError:
            with open(file_path, 'w') as f:
                f.write("0")
            return 0  # if unable to read the high score file, create a new one and set score = 0

    def write_high_score(self):
        file_path = os.path.dirname(__file__) + "/resources/high_score.txt"
        try:
            with open(file_path, 'w') as f:
                f.write(str(self.high_score))
        except IOError:
            print("Error writing to High score file")

    def show_score_banner(self):
        if self.is_new_high_score():
            self.high_score = self.current_score
            hs_banner = self.font.render(f"New High Score!", True, WHITE)
            self.parent_screen.blit(hs_banner, (200, 250))
            self.write_high_score()

        score_banner = self.font.render(f"Game Over! Your score is: {self.current_score}", True, WHITE)
        self.parent_screen.blit(score_banner, (200, 300))


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Play Snake by Alex Schwartz")

        pygame.mixer.init()
        self.play_bg_music()
        self.clock_speed = MEDIUM_SPEED  # default medium
        self.block_size = 40  # blocks are 40x40 pixels

        self.surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.snake = Snake(self.surface, LENGTH_OF_SNAKE, self.block_size)
        self.snake.draw()
        self.wall = Wall(self.surface, self.block_size)
        self.current_map = 0
        self.wall.change_map(self.current_map)
        self.wall.draw()
        self.apple = Apple(self.surface, self.block_size)
        self.apple_valid = False
        self.valid_apple_move()
        self.apple.draw()
        self.render_background()
        self.refresh_count = 0
        self.change_direction = False
        self.score_board = ScoreBoard(self.surface, self.snake.length)

        self.mute = 0
        self.menu()

    def toggle_music(self):
        if self.mute == 0:
            pygame.mixer.music.pause() if pygame.mixer.music.play() else pygame.mixer.music.play()
        else:
            pygame.mixer.music.pause()

    def is_collision(self, x1, y1, x2, y2):
        if x1 == x2 and y1 == y2:
            return True
        return False

    def eat(self):
        # snake collides with apple
        if self.is_collision(self.snake.x[0], self.snake.y[0], self.apple.x, self.apple.y):
            self.play_sound('ding')
            self.snake.increase_length()
            self.apple_valid = False
            self.valid_apple_move()

    def valid_apple_move(self):
        while not self.apple_valid:  # move apple until it's not placed inside snake
            self.apple.move()
            self.apple_valid = self.is_apple_valid()

    def is_apple_valid(self):
        for i in range(self.snake.length):
            if self.is_collision(self.apple.x, self.apple.y, self.snake.x[i], self.snake.y[i]):  # apple is inside snake
                return False
        if (self.apple.x, self.apple.y) in self.wall.walls:  # if apple is inside the walls
            return False
        return True

    def is_game_over(self):
        # snake collides with itself
        for i in range(3, self.snake.length):
            if self.is_collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                self.play_sound("crash")
                raise "Game Over"
        if not ((self.block_size <= self.snake.x[0] <= (MAX_X * self.block_size)) and (self.block_size <= self.snake.y[0] <= (MAX_Y * self.block_size))):
            self.play_sound("crash")
            raise "Hit The Boundaries"

        for square in self.wall.walls:  # if collision with walls
            if self.is_collision(self.snake.x[0], self.snake.y[0], square[0],square[1]):
                self.play_sound("crash")
                raise "Game Over"
        if self.snake.length - 2 >= ((MAX_Y + 1) * (MAX_X + 1) - len(self.wall.walls)): # WIP fix game win crash
            self.play_sound("ding")
            print("You WON!!!")
            raise "You WON!!!"

    def show_game_over(self):
        self.render_background()
        font = pygame.font.SysFont('arial', 30)
        self.score_board.calculate_score(self.snake.length)
        self.score_board.show_score_banner()

        line2 = font.render("To play again, press Enter. To Exit, press Escape", True, WHITE)
        self.surface.blit(line2, (200, 350))
        pygame.display.update()

    def reset(self):
        self.snake = Snake(self.surface, LENGTH_OF_SNAKE, self.block_size)
        self.apple = Apple(self.surface, self.block_size)
        self.apple_valid = 0
        self.valid_apple_move()

    def play_sound(self, sound):
        sound = pygame.mixer.Sound(f"resources/{sound}.mp3")
        pygame.mixer.Sound.play(sound)

    def play_bg_music(self):
        pygame.mixer.music.load("resources/bg_music_1.mp3")
        pygame.mixer.music.play()

    def draw_grid(self):
        for x in range(0, WINDOW_WIDTH, self.block_size):
            for y in range(0, WINDOW_WIDTH, self.block_size):
                rect = pygame.Rect(x, y, self.block_size, self.block_size)
                pygame.draw.rect(self.surface, BLACK, rect, 1)

    def render_background(self):
        bg = pygame.image.load("resources/background.jpg")
        self.surface.blit(bg, (0, 0))

    def is_ready_to_render(self):
        refresh_rate = 0
        if self.refresh_count == refresh_rate:
            self.refresh_count = 0
            return True
        else:
            self.refresh_count += 1
            return False

    def play(self):
        self.render_background()
        self.draw_grid()
        if self.is_ready_to_render():
            self.snake.walk()
            self.is_game_over()
            self.change_direction = False
        else:
            self.snake.draw()
        self.apple.draw()
        self.wall.draw()
        self.score_board.calculate_score(self.snake.length)
        self.score_board.draw()
        self.eat()
        pygame.display.update()

    def menu(self):
        bg_menu = pygame.image.load("resources/menu.jpg")
        self.surface.blit(bg_menu, (0, 0))
        font = pygame.font.SysFont('arial', 50, bold=True)
        title = font.render(f"SNAKE", True, BLACK)
        self.surface.blit(title, (400, 150))
        author = font.render(f"by Alexander Schwartz", True, BLACK)
        self.surface.blit(author, (280, 200))
        font = pygame.font.SysFont('arial', 30)
        tag_line = font.render(f"Choose your difficulty", True, WHITE)
        self.surface.blit(tag_line, (360, 350))
        speeds = font.render(f"1 = Slow   2 = Medium   3 = Fast   0 = Impossible", True, WHITE)
        self.surface.blit(speeds, (240, 400))
        line2 = font.render("To Play, press Enter or press a number to choose your speed.", True, WHITE)
        self.surface.blit(line2, (160, 500))
        exit_line = font.render("Press A to switch the map", True, WHITE)
        self.surface.blit(exit_line, (360, 550))
        exit_line = font.render("To Exit, press Escape. Press M to Mute Music.", True, WHITE)
        self.surface.blit(exit_line, (240, 600))
        footer = font.render('Programmed using python and pygame library by Alexander Schwartz "Just for fun"', True, WHITE)
        self.surface.blit(footer, (40, 750))
        self.score_board.calculate_score(self.snake.length)
        self.score_board.draw()
        pygame.display.update()

    def pause_game(self):
        font = pygame.font.SysFont('arial', 50, bold=True)
        title = font.render(f"PAUSED", True, WHITE)
        self.surface.blit(title, (400, 450))
        pygame.display.update()

    def change_speed_reset(self, speed):
        self.clock_speed = speed
        self.reset()

    def run(self):
        running = True
        pause = True
        clock = pygame.time.Clock()

        while running:
            clock.tick(self.clock_speed)

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_m:  # toggle mute music
                        self.mute = (1 if self.mute == 0 else 0)
                        self.toggle_music()

                    if event.key == K_RETURN:
                        if pause:
                            pause = False
                        else:
                            pause = True
                            self.pause_game()

                    if pause:
                        if event.key == K_1:
                            self.change_speed_reset(5)
                            pause = False
                        elif event.key == K_2:
                            self.change_speed_reset(MEDIUM_SPEED)
                            pause = False
                        elif event.key == K_3:
                            self.change_speed_reset(13)
                            pause = False
                        elif event.key == K_0:
                            self.change_speed_reset(20)
                            pause = False
                        elif event.key == K_EQUALS: # Hidden increase speed function
                            self.clock_speed += 1
                        elif event.key == K_MINUS: # Hidden lower speed function
                            if self.clock_speed > 1:
                                self.clock_speed -= 1
                        elif event.key == K_a:
                            self.current_map += 1
                            if self.current_map == len(self.wall.map_dict):
                                self.current_map = 0
                            self.wall.change_map(self.current_map)
                            self.wall.draw()

                    else:

                        if (event.key == K_UP) & (self.snake.direction != 'down') & (not self.change_direction):
                            self.snake.move_up()
                            self.change_direction = True
                        elif (event.key == K_DOWN) & (self.snake.direction != 'up') & (not self.change_direction):
                            self.snake.move_down()
                            self.change_direction = True
                        elif (event.key == K_LEFT) & (self.snake.direction != 'right') & (not self.change_direction):
                            self.snake.move_left()
                            self.change_direction = True
                        elif (event.key == K_RIGHT) & (self.snake.direction != 'left') & (not self.change_direction):
                            self.snake.move_right()
                            self.change_direction = True

                elif event.type == QUIT:
                    running = False

            try:
                if not pause:
                    self.play()
            except Exception as e:
                self.show_game_over()
                self.toggle_music()
                pause = True
                self.reset()


if __name__ == "__main__":
    game = Game()
    game.run()
