import numpy as np
import os
import sys


class MapDictionary:

    def __init__(self, max_x, max_y):
        self.max_x = max_x
        self.max_y = max_y
        self.map_dict = {
            0: self.blank_map(),
            1: self.equality(),
            2: self.load_map_file("cross.txt"),
            3: self.load_map_file("corners.txt"),
            4: self.load_map_file("crosshair.txt")}

    def map_test(self):
        # test map for debugging, nearly full of walls
        test_map = np.ones((self.max_x + 1, self.max_y + 1), dtype=np.uint8)

        test_map[1:-1, 1:self.max_y // 2 + 2] = 0  # build the top half of the walls
        test_map[15:-1, self.max_y // 2 - 2: self.max_y // 2 + 2] = 1  # build the middle right side of walls
        test_map[0:self.max_x, 0:self.max_y // 3 + 3] = 1  # build the bottom half of walls
        return test_map

    def blank_map(self):
        map_walls = np.ones((self.max_y + 1, self.max_x + 1), dtype=np.uint8)
        map_walls[1:-1, 1:-1] = 0
        return map_walls

    def equality(self):
        map_walls = np.ones((self.max_x + 1, self.max_y + 1), dtype=np.uint8)
        map_walls[1:-1, 1:-1] = 0
        map_walls[5:-5, self.max_y // 3] = 1
        map_walls[5:-5, -self.max_y // 3] = 1
        return map_walls

    def load_map_file(self, filename):
        file_path = os.path.dirname(__file__) + "/resources/" + filename
        try:
            map_walls = []
            with open(file_path, 'r') as f:
                for line in f.readlines():
                    if len(map_walls) == 0:  # initialize the array with first line
                        values = np.array([int(line, 2)], dtype=np.uint32)  # encode the line into uint32
                        view = values.view(dtype=np.uint8)  # cut the uint 32 into 4 pieces uint8 so unpackbits works

                        # force little endian order, so it can decode properly if not already set
                        if values.dtype.byteorder == '>' or (values.dtype.byteorder == '=' and sys.byteorder == 'big'):
                            view = view[::-1]  # reverse the order

                        decoded_line = np.unpackbits(view, count=self.max_x + 1, bitorder='little')[::-1]  # decoded solution
                        map_walls = decoded_line
                    else:  # add each row of the file to the array line by line
                        values = np.array([int(line, 2)], dtype=np.uint32)
                        view = values.view(dtype=np.uint8)

                        decoded_line = np.unpackbits(view, count=self.max_x + 1, bitorder='little')[::-1]
                        map_walls = np.vstack((map_walls, decoded_line))  # stack each new row at the end of the array
                return map_walls
        except IOError:
            print(IOError)
            return self.blank_map()