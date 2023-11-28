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
# Add display text for current map and speed settings
# add separate high scores for each map
# save high scores to a database
# add 2 player support
# host application online, save a record of high score of all players
# fix game win crash
# develop AI snake that can win the game every time in the shortest amount of time possible
# Implement Multithreading to improve performance. (It seems like game clock slows down randomly)
# Speed and resource optimization, improve performance when snake is very long
# Separate scoreboard and score calculation classes
# Add score multiplier based on map and speed and display multiplier
# Add event queue for changing directions, log the first 2 or 3 keystrokes and execute the next one in game.play
# Add noise when the bonus appears

from pygame.locals import *

from food import *
from snake import *
from ScoreBoard import *
from GameMap import *
from Wall import *
from timer import *
from multiprocessing import Process, Queue


# block image file is 40 x 40 pixels
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
MAX_X = 24
MAX_Y = 19
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800

LENGTH_OF_SNAKE = 4
SLOW_SPEED = 5
MEDIUM_SPEED = 9
FAST_SPEED = 13
IMPOSSIBLE_SPEED = 20


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Play Snake by Alex Schwartz")

        pygame.mixer.init()
        self.play_bg_music()
        self.clock_speed = MEDIUM_SPEED  # default medium
        self.update_speed_info()
        self.block_size = 40  # blocks are 40x40 pixels

        self.surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.snake = Snake(self.surface, LENGTH_OF_SNAKE, self.block_size)
        self.snake.draw()

        self.wall = Wall(self.surface)
        self.current_map = 0
        self.game_map = GameMap(self.block_size)
        self.draw_map()

        self.apple = Apple(self.surface, self.block_size)
        self.apple_valid = False
        self.star = Star(self.surface, self.block_size)
        self.star_valid = False
        self.valid_food_move(self.apple)
        self.apple.draw()
        self.bonus_count = 0
        self.bonus_timer = -1

        self.render_background()
        self.refresh_count = 0
        self.change_direction = False

        self.score_board = ScoreBoard(self.surface, self.snake.length, LENGTH_OF_SNAKE)
        self.timer_display = TimerDisplay(self.surface, self.bonus_timer)
        self.default_font = pygame.font.SysFont('arial', 30)

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
        # snake collides with food
        for food in [self.apple, self.star]:
            if self.is_collision(self.snake.x[0], self.snake.y[0], food.x, food.y):
                self.snake.increase_length()

                self.bonus_count += 1
                if isinstance(food, Apple):
                    self.apple_valid = False
                    self.play_sound('ding')
                    self.valid_food_move(food)
                elif isinstance(food, Star):
                    self.play_sound('bonus_ding')
                    self.snake.increase_length()  # bonus length
                    self.star_valid = False
                    food.remove()
                    self.bonus_timer_off()

    def valid_food_move(self, food):
        if food == self.apple:
            while not self.apple_valid:  # move apple until it's not placed inside snake or star
                food.move()
                self.apple_valid = self.is_food_valid(food)
        elif food == self.star:
            while not self.star_valid:  # move star until it's not placed inside snake or apple
                food.move()
                self.star_valid = self.is_food_valid(food)

    def is_food_valid(self, food):
        for i in range(self.snake.length):
            if self.is_collision(food.x, food.y, self.snake.x[i], self.snake.y[i]):  # apple is inside snake
                return False
        if (food.x, food.y) in self.game_map.walls:  # if apple is inside the walls
            return False
        elif isinstance(food, Apple):
            if self.is_collision(food.x, food.y, self.star.x, self.star.y):  # apple inside star
                return False
        elif isinstance(food, Star):
            if self.is_collision(food.x, food.y, self.apple.x, self.apple.y):  # star inside apple
                return False
        return True

    def bonus_timer_on(self):
        return True if self.bonus_timer >= 0 else False

    def bonus_timer_off(self):
        self.bonus_timer = -1
        self.expire_bonus()
        # turn off display

    def tick_bonus_timer(self):
        self.bonus_timer -= 1
        self.timer_display.display(self.bonus_timer)  # turn on timer display

        if self.bonus_timer <= 0:
            self.bonus_timer_off()

    def expire_bonus(self):
        """ When the timer runs out, the bonus disappears"""
        self.star.remove()
        self.star_valid = False

    def activate_bonus(self):
        """
        The snake bonus star appears after a max of 7 apples are eaten. After 4 are eaten, there a random number
        0-4 is added to the timer.
        """
        if self.bonus_count == 4:
            self.bonus_count += r.randint(0, 4)  # the bonus spawns after a random number of times based on this

        if self.bonus_count >= 7:
            self.valid_food_move(self.star)
            self.bonus_count = 0
            self.bonus_timer = 40

    def draw_map(self):
        for wall_xy in self.game_map.walls:
            self.wall.draw(wall_xy)

    def sfx_game_over(self):
        return self.play_sound("pixel_death")

    def is_game_over(self):
        # snake collides with itself
        for i in range(3, self.snake.length):
            if self.is_collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                self.sfx_game_over()
                raise "Game Over"
        if not ((self.block_size <= self.snake.x[0] <= (MAX_X * self.block_size)) and (self.block_size <= self.snake.y[0] <= (MAX_Y * self.block_size))):
            self.sfx_game_over()
            raise "Hit The Boundaries"

        for square in self.game_map.walls:  # if collision with walls
            if self.is_collision(self.snake.x[0], self.snake.y[0], square[0], square[1]):
                self.sfx_game_over()
                raise "Game Over"
        if self.snake.length - 2 >= ((MAX_Y + 1) * (MAX_X + 1) - len(self.game_map.walls)):  # WIP fix game win crash
            self.play_sound("bonus_ding")
            print("You WON!!!")
            raise "You WON!!!"

    def show_game_over(self):
        self.render_background()
        self.score_board.calculate_score(self.snake.length)
        self.score_board.show_score_banner()

        line2 = self.default_font.render("To play again, press Enter. To Exit, press Escape", True, WHITE)
        self.surface.blit(line2, (200, 350))
        pygame.display.update()

    def reset(self):
        self.snake = Snake(self.surface, LENGTH_OF_SNAKE, self.block_size)
        self.apple = Apple(self.surface, self.block_size)
        self.apple_valid = False
        self.star_valid = False
        self.star.remove()
        self.valid_food_move(self.apple)
        self.bonus_count = 0
        self.bonus_timer = -1

    def play_sound(self, sound):
        sound = pygame.mixer.Sound(f"resources/{sound}.mp3")
        pygame.mixer.Sound.play(sound)

    def play_bg_music(self):
        pygame.mixer.music.load("resources/Brilliant_notes.mp3")
        pygame.mixer.music.play()

    def draw_grid(self):
        for x in range(0, WINDOW_WIDTH, self.block_size):
            for y in range(0, WINDOW_HEIGHT, self.block_size):
                rect = pygame.Rect(x, y, self.block_size, self.block_size)
                pygame.draw.rect(self.surface, BLACK, rect, 1)

    def draw_map_info(self):
        info_map = self.default_font.render(f"Map :  {self.game_map.current_map_name}", True, WHITE)
        self.surface.blit(info_map, (325, 760))

    def draw_speed_info(self):
        info_speed = self.default_font.render(f"Speed : {self.speed_info} :  {self.clock_speed}", True, WHITE)
        self.surface.blit(info_speed, (45, 760))

    def update_speed_info(self):
        if self.clock_speed < SLOW_SPEED:
            speed = "Very Slow"
        elif self.clock_speed < MEDIUM_SPEED:
            speed = "Slow"
        elif self.clock_speed < FAST_SPEED:
            speed = "Medium"
        elif self.clock_speed < IMPOSSIBLE_SPEED:
            speed = "Fast"
        else:
            speed = "Impossible"
        self.speed_info = speed

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
        self.star.draw()
        self.draw_map()
        self.score_board.calculate_score(self.snake.length)
        self.score_board.draw()
        self.eat()
        if self.bonus_timer_on():
            self.tick_bonus_timer()
        self.activate_bonus()
        self.draw_map_info()
        self.draw_speed_info()

        pygame.display.update()

    def menu(self):
        bg_menu = pygame.image.load("resources/menu.jpg")
        self.surface.blit(bg_menu, (0, 0))
        font = pygame.font.SysFont('arial', 50, bold=True)
        title = font.render(f"SNAKE", True, BLACK)
        self.surface.blit(title, (400, 150))
        author = font.render(f"by Alexander Schwartz", True, BLACK)
        self.surface.blit(author, (280, 200))
        font = self.default_font
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
        self.surface.blit(title, (420, 350))
        pygame.display.update()

    def change_speed_reset(self, speed):
        self.clock_speed = speed
        self.update_speed_info()
        self.reset()

    def get_event(self, event_queue):
        pass

    def put_event(self, event_queue):
        pass

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
                            self.change_speed_reset(SLOW_SPEED)
                            pause = False
                        elif event.key == K_2:
                            self.change_speed_reset(MEDIUM_SPEED)
                            pause = False
                        elif event.key == K_3:
                            self.change_speed_reset(FAST_SPEED)
                            pause = False
                        elif event.key == K_0:
                            self.change_speed_reset(IMPOSSIBLE_SPEED)
                            pause = False
                        elif event.key == K_EQUALS:  # Hidden increase speed function
                            self.clock_speed += 1
                        elif event.key == K_MINUS:  # Hidden lower speed function
                            if self.clock_speed > 1:
                                self.clock_speed -= 1
                        elif event.key == K_a:
                            self.current_map += 1
                            if self.current_map == len(self.game_map.map_instance.map_dict):
                                self.current_map = 0
                            self.game_map.change_map(self.current_map)
                            self.draw_map()
                            self.reset()

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
                elif pause:
                    self.update_speed_info()
                    self.draw_speed_info()
            except Exception as e:
                self.show_game_over()
                self.toggle_music()
                pause = True
                self.reset()


if __name__ == "__main__":
    # Create a multiprocessing Queue to communicate between processes
    # Have a maximum inputs in the queue to prevent overflow
    input_queue = Queue(maxsize=5)

    # Create a game process
    #game_process = Process(target=Game(input_queue.run())

    # Start process
    #game_process.start()

    # Main process to handle user input


    game = Game()

    game.run()