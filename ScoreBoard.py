import os
import pygame


WHITE = (255, 255, 255)


class ScoreBoard:
    def __init__(self, parent_screen, length, default_length):
        self.parent_screen = parent_screen
        self.current_score = length
        self.high_score = self.read_high_score()
        self.font = pygame.font.SysFont('arial', 30)  # default font for scores
        self.start_length = default_length

    def calculate_score(self, length):
        self.current_score = length - self.start_length
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
