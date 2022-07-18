"""
Generate Map files for snake:
The default creates a blank map, however, anything can be created similarly to blank_map
Also once the blank file is generated, it can be edited in the text editor
Walls = 1
Empty space = 0

NOTE: The map text file is transposed when loaded into main
"""

import os
import numpy as np


MAX_X = 24
MAX_Y = 19


class MapGenerator:

    def __init__(self, fname, x_limit, y_limit):
        self.filename = fname
        self.x_limit = x_limit
        self.y_limit = y_limit

    def blank_map(self):
        map_walls = np.ones((self.y_limit + 1, self.x_limit + 1), dtype=np.uint8)
        map_walls[1:-1, 1:-1] = 0
        return map_walls

    def generate_map(self):
        file_path = os.path.dirname(__file__) + "/resources/" + self.filename

        try:
            with open(file_path, 'w') as f:
                write_str = "".join(char for char in str(self.blank_map()) if char.isdigit() or char == "\n")
                f.write(write_str)
            with open(file_path, 'r') as f:  # for testing purposes
                print(f.read())

        except IOError:
            print("Error opening file")


if __name__ == "__main__":
    generator = MapGenerator('test.txt', MAX_X, MAX_Y)
    generator.generate_map()