import map_dictionary
import numpy as np


MAX_X = 24
MAX_Y = 19


class GameMap:
    # Builds the list of wall coordinates for the map/game board
    def __init__(self, block_size):
        self.block_size = block_size
        self.walls = []
        self.map_instance = map_dictionary.MapDictionary(MAX_X, MAX_Y)  # generates map array by loading from map files
        self.change_map(0)

    def build_map(self, map_blueprint):
        walls_x, walls_y = np.nonzero(map_blueprint)
        walls_y *= self.block_size
        walls_x *= self.block_size
        self.walls = list(zip(walls_y, walls_x))

    def change_map(self, selected_map):
        current_map_blueprint = self.map_instance.map_dict.get(selected_map)
        self.build_map(current_map_blueprint)
