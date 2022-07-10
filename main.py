"""
Snake: Programmed by Alexander Schwartz
Based on the classic nokia snake game, programmed in python

Choose your difficulty:
1 = Slow   2 = Medium   3 = Fast   0 = Impossible
To Play, press Enter or press a number to choose your speed.
To Exit, press Escape

Programmed using python and pygame library by Alexander Schwartz "Just for fun"
"""

# TO DO:
# fix snake shape, so it is a clear path from head to tail
# make snake movement smoother
# improve snake block images
# add map import using a txt file -- so map is loaded from a file, any new map can easily be added and used.
# add mouse interface in menu
# save high score stat for next time application is opened
# add 2 player support
# host application online, save a record of high score of all players
# fix main menu overwriting game over screen when pressing directional buttons
# add paused text when game is paused during gameplay
# fix game win crash


import pygame
from pygame.locals import *
import random as r
import numpy as np

SIZE = 40  # block image file is 40 x 40 pixels
BACKGROUND_COLOR = (0x16, 0x36, 0x93)
WALL_COLOR = (0, 0, 0)
WHITE = (255,255,255)
# corners  => (0,0), (24,0), (0,19), (24,19)
MAX_X = 24
MAX_Y = 19
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
REFRESH_RATE = 0
LENGTH_OF_SNAKE = 4
MEDIUM_SPEED = 9


class Wall:
    def __init__(self, parent_screen):
        self.wall = pygame.image.load("resources/wall.jpg").convert()
        self.parent_screen = parent_screen
        self.x = [SIZE]
        self.y = [SIZE]
        self.walls = []

    def map_test(self):
        # test map for debugging
        test_map = np.ones((MAX_X + 1, MAX_Y + 1))
        test_map[1:-1, 1:MAX_Y // 2 + 2] = 0

        test_map[15:-1, MAX_Y // 2 - 2: MAX_Y // 2 + 2] = 1
        test_map[0:MAX_X, 0:MAX_Y // 3 + 3] = 1
        return test_map

    def blank_map(self):

        map = np.ones((MAX_X+1, MAX_Y+1))
        map[1:-1, 1:-1] = 0
        return map

    def horizontal_map(self):

        map = np.ones((MAX_X+1, MAX_Y+1))
        map[1:-1, 1:-1] = 0
        map[4:-4, MAX_Y // 3] = 1
        map[4:-4, -MAX_Y // 3 - 1] = 1
        return map

    def build_map(self, map_blueprint):
        walls_x, walls_y = np.nonzero(map_blueprint)
        walls_y *= SIZE
        walls_x *= SIZE
        self.walls = list(zip(walls_x,walls_y))

    def draw(self,selected_map):
        if selected_map == 0:
            current_map = self.blank_map()
        elif selected_map == 1:
            current_map = self.horizontal_map()
        else:
            current_map = self.map_test()

        self.build_map(current_map)

        for current_pos in self.walls:
            self.parent_screen.blit(self.wall, current_pos) # draw wall block image


class Apple:
    def __init__(self, parent_screen):
        self.image = pygame.image.load("resources/apple.jpg").convert()
        self.parent_screen = parent_screen
        self.x = 0  # apple starting position x
        self.y = 0  # apple starting position y

    def move(self):
        self.x = r.randint(1, 23) * SIZE
        self.y = r.randint(1, 18) * SIZE

    def draw(self):
        self.parent_screen.blit(self.image, (self.x, self.y))  # draw apple


class Snake:
    def __init__(self, parent_screen, length):
        self.x_block = pygame.image.load("resources/x_block.jpg").convert()
        self.y_block = pygame.image.load("resources/snake_block_2.jpg").convert()
        self.head_block = pygame.image.load("resources/head_block2.jpg").convert()
        self.tail_block = pygame.image.load("resources/tail_block.jpg").convert()
        self.x = [SIZE * 5] * length
        self.y = [SIZE * 9] * length
        self.parent_screen = parent_screen
        self.direction = 'right'
        self.length = length

    def increase_length(self):
        self.length += 1
        self.x.append(-1)
        self.y.append(-1)

    def draw(self):
        self.parent_screen.blit(self.head_block, (self.x[0], self.y[0]))  # draw head
        for i in range(1, self.length - 1, 2): # every other normal
            if self.direction == 'left' or self.direction == 'right':  # WIP change block image to show shape of snake
                self.parent_screen.blit(self.x_block, (self.x[i], self.y[i]))
            else:
                self.parent_screen.blit(self.x_block, (self.x[i], self.y[i]))
        for i in range(2, self.length - 1, 2): # every other black
            if self.direction == 'left' or self.direction == 'right':  # WIP change block image to show shape of snake
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
            self.x[0] -= SIZE
        elif self.direction == 'right':
            self.x[0] += SIZE
        elif self.direction == 'down':
            self.y[0] += SIZE
        elif self.direction == 'up':
            self.y[0] -= SIZE
        self.draw()


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Play Snake by Alex Schwartz")

        pygame.mixer.init()
        self.play_bg_music()

        self.surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.snake = Snake(self.surface, LENGTH_OF_SNAKE)
        self.snake.draw()
        self.wall = Wall(self.surface)
        self.current_map = 0
        self.wall.draw(self.current_map)
        self.apple = Apple(self.surface)
        self.apple_valid = False
        self.valid_apple_move()
        self.apple.draw()
        self.render_background()
        self.refresh_count = 0
        self.change_direction = False
        self.high_score = 0
        self.mute = 0
        self.menu()

    def toggle_music(self):
        if self.mute == 0:
            pygame.mixer.music.pause() if pygame.mixer.music.play() else pygame.mixer.music.play()
        else:
            pygame.mixer.music.pause()

    def display_score(self):
        font = pygame.font.SysFont('arial', 30)
        score = font.render(f"Score: {self.snake.length - LENGTH_OF_SNAKE}", True, WHITE)
        self.surface.blit(score, (600, 0))
        high_score = font.render(f"High Score: {self.high_score}", True, WHITE)
        self.surface.blit(high_score, (800, 0))

    def is_collision(self, x1, y1, x2, y2):
        if x1 == x2 and y1 == y2:
            return True
        return False

    def show_game_over(self):
        self.render_background()
        font = pygame.font.SysFont('arial', 30)

        if self.high_score < self.snake.length:
            self.high_score = self.snake.length
            high_score = font.render(f"New High Score!", True, WHITE)
            self.surface.blit(high_score, (200, 250))

        score = font.render(f"Game Over! Your score is: {self.snake.length}", True, WHITE)
        self.surface.blit(score, (200, 300))
        line2 = font.render("To play again, press Enter. To Exit, press Escape", True, WHITE)
        self.surface.blit(line2, (200, 350))
        pygame.display.update()

    def reset(self):
        self.snake = Snake(self.surface, LENGTH_OF_SNAKE)
        self.apple = Apple(self.surface)
        self.apple_valid = 0
        self.valid_apple_move()
        self.toggle_music()

    def play_sound(self, sound):
        sound = pygame.mixer.Sound(f"resources/{sound}.mp3")
        pygame.mixer.Sound.play(sound)

    def play_bg_music(self):
        pygame.mixer.music.load("resources/bg_music_1.mp3")
        pygame.mixer.music.play()

    def draw_grid(self):
        block_size = SIZE
        for x in range(0, WINDOW_WIDTH, SIZE):
            for y in range(0, WINDOW_WIDTH, SIZE):
                rect = pygame.Rect(x, y, block_size, block_size)
                pygame.draw.rect(self.surface, WALL_COLOR, rect, 1)

    def render_background(self):
        bg = pygame.image.load("resources/background.jpg")
        self.surface.blit(bg, (0, 0))

    def is_ready_to_render(self):
        if self.refresh_count == REFRESH_RATE:
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
        self.wall.draw(self.current_map)
        self.display_score()
        pygame.display.update()

        self.eat()

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
            if (self.apple.x == self.snake.x[i]) & (self.apple.y == self.snake.y[i]):  # if apple is inside snake
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
        if not ((SIZE <= self.snake.x[0] <= (MAX_X * SIZE) - SIZE) and (SIZE <= self.snake.y[0] <= (MAX_Y * SIZE) - SIZE)):
            self.play_sound("crash")
            raise "Hit The Boundaries"

        for square in self.wall.walls:  # if collision with walls
           if self.is_collision(self.snake.x[0], self.snake.y[0], square[0],square[1]):
                self.play_sound("crash")
                raise "Game Over"

    def menu(self):
        self.render_background()
        font = pygame.font.SysFont('arial', 50)
        title = font.render(f"SNAKE", True, WHITE)
        self.surface.blit(title, (400, 200))
        author = font.render(f"by Alexander Schwartz", True, WHITE)
        self.surface.blit(author, (280, 250))
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
        self.display_score()
        pygame.display.update()

    def run(self):
        running = True
        pause = True
        clock = pygame.time.Clock()
        clock_speed = MEDIUM_SPEED # default medium

        while running:
            clock.tick(clock_speed)

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if (event.key == K_m): # toggle mute music
                            self.mute = (1 if self.mute == 0 else 0)
                            self.toggle_music()

                    if event.key == K_RETURN:
                        if pause == True:
                            self.toggle_music()
                            pause = False
                        else:
                            self.toggle_music()
                            pause = True

                    if pause:
                        self.menu()
                        self.toggle_music()
                        if event.key == K_1:
                            clock_speed = 5
                            pause = False
                            self.toggle_music()
                            self.reset()
                        elif event.key == K_2:
                            clock_speed = MEDIUM_SPEED
                            pause = False
                            self.toggle_music()
                            self.reset()
                        elif event.key == K_3:
                            clock_speed = 13
                            pause = False
                            self.toggle_music()
                            self.reset()
                        elif event.key == K_0:
                            clock_speed = 20
                            pause = False
                            self.toggle_music()
                            self.reset()
                        elif event.key == K_EQUALS: # Hidden increase speed function
                            clock_speed += 1
                        elif event.key == K_MINUS: # Hidden lower speed function
                            if clock_speed > 1:
                                clock_speed -= 1
                        elif event.key == K_a:
                            self.current_map += 1
                            if self.current_map == 5:
                                self.current_map = 0
                            self.wall.draw(self.current_map)



                    else:

                        if (event.key == K_UP) & (self.snake.direction != 'down') & (self.change_direction == False):
                            self.snake.move_up()
                            self.change_direction = True
                        elif (event.key == K_DOWN) & (self.snake.direction != 'up') & (self.change_direction == False):
                            self.snake.move_down()
                            self.change_direction = True
                        elif (event.key == K_LEFT) & (self.snake.direction != 'right') & (self.change_direction == False):
                            self.snake.move_left()
                            self.change_direction = True
                        elif (event.key == K_RIGHT) & (self.snake.direction != 'left') & (self.change_direction == False):
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
