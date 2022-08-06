from queue import Queue


class EventQueue(Queue):

    def get_event(self):
        action = self.get()

        if action == "move up":
            self.snake.move_up()
        elif action == "move down":
            self.snake.move_down()
    


