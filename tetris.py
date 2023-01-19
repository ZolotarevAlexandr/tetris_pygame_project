import pygame
import sys
from random import choice

blocks = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]]
]

cell_size = 18
cols = 10
rows = 22
FPS = 30


def create_board():
    board = [0 for x in range(cols)
             for y in range(rows)]
    return board


def rotate_clockwise(block):
    return [
        [block[y][x] for y in range(len(block))]
        for x in range(len(block[0]) - 1, -1, -1)
    ]


def destroy_filed_lines(board):
    new_board = board.copy()
    for line in board:
        if line.count('0') == 0:
            del new_board[new_board.index(line)]
            new_board.insert(0, ['0'] * 10)
    return new_board


def quit_game():
    sys.exit()


class Tetris:
    def __init__(self):
        pygame.init()
        self.width = cell_size * (cols + 6)
        self.height = cell_size * rows
        self.rlim = cell_size * cols
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.next_block = choice(blocks)
        self.board = create_board()
        self.new_block()
        self.level = 1
        self.score = 0
        self.lines = 0

        self.game_over = False

    def new_block(self):
        self.block = self.next_block[:]
        self.next_block = choice(blocks)
        self.block_x = int(cols / 2 - len(self.block[0]) / 2)
        self.block_y = 0

        if self.check_collision():
            self.game_over = True

    def move_block(self, movement):
        if not self.game_over:
            new_x = self.block_x + movement
            if new_x < 0:
                new_x = 0
            if new_x > cols - len(self.block[0]):
                new_x = cols - len(self.block[0])

            if not self.check_collision():
                self.block_x = new_x

    def rotate(self):
        rotated_block = rotate_clockwise(self.block)
        if not self.check_collision():
            self.block = rotated_block

    def new_game(self):
        if self.game_over:
            self.board = create_board()
            self.new_block()
            self.level = 1
            self.score = 0
            self.lines = 0
            self.game_over = False

    def drop(self):
        self.block_y += 1
        if self.check_collision():
            self.new_block()
            self.board = destroy_filed_lines(self.board)
            return True
        return False

    def check_collision(self):
        pass
