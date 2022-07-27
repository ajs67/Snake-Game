import pygame


WHITE = (255, 255, 255)


class TimerDisplay:

    def __init__(self, parent_screen, time):
        self.parent_screen = parent_screen
        self.time = time
        self.font = pygame.font.SysFont('arial', 30)

    def display(self, current_time):
        self.time = current_time
        if self.time >= 0:
            self.draw()

    def draw(self):
        time_remaining = self.font.render(f"Bonus Time: {self.time}", True, WHITE)
        self.parent_screen.blit(time_remaining, (100, 0))
