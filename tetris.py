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

colors = (
    (0, 0, 0),
    (0, 119, 211), # blue
    (72, 93, 197), # dark blue
    (120, 37, 111), # purple
    (234, 20, 28), # red
    (254, 251, 52), # yellow
    (83, 218, 63), # green
    (255, 200, 46) # orange
)

cell_size = 18
cols = 10
rows = 22
FPS = 30
drop_event = pygame.USEREVENT + 1


def create_board():
    board = [[0 for x in range(cols)]
             for y in range(rows)]
    return board


def rotate_clockwise(block):
    return [
        [block[y][x] for y in range(len(block))]
        for x in range(len(block[0]) - 1, -1, -1)
    ]


def destroy_filed_lines(board):
    cleared_lines = 0
    bonus = [0, 100, 300, 600, 1200]
    new_board = board.copy()
    for line in board:
        if line.count(0) == 0:
            del new_board[new_board.index(line)]
            new_board.insert(0, [0] * cols)
            cleared_lines += 1
    if cleared_lines > len(bonus):
        bonus_points = bonus[-1]
    else:
        bonus_points = bonus[cleared_lines]
    return new_board, bonus_points


def join_block(board, block_list, coords):
    block_x, block_y = coords
    for y, row in enumerate(block_list):
        for x, val in enumerate(row):
            board[y + block_y - 1][x + block_x] += val
    return board


def check_collision(board, shape, coords):
    block_x, block_y = coords
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            try:
                if cell and board[y + block_y][x + block_x]:
                    return True
            except IndexError:
                return True
    return False


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
        self.paused = False

        pygame.time.set_timer(drop_event, 1000 // self.level)
        pygame.key.set_repeat(250, 25)

    def new_block(self):
        self.block = self.next_block[:]
        self.next_block = choice(blocks)
        self.block_x = int(cols / 2 - len(self.block[0]) / 2)
        self.block_y = 0

        if check_collision(self.board, self.block, (self.block_x, self.block_y)):
            self.game_over = True
            print('Game Over!')

    def move_block(self, movement):
        if not (self.game_over or self.paused):
            new_x = self.block_x + movement
            if new_x < 0:
                new_x = 0
            if new_x > cols - len(self.block[0]):
                new_x = cols - len(self.block[0])

            if not check_collision(self.board, self.block, (new_x, self.block_y)):
                self.block_x = new_x

    def rotate(self):
        if not (self.game_over or self.paused):
            rotated_block = rotate_clockwise(self.block)
            if not check_collision(self.board, rotated_block, (self.block_x, self.block_y)):
                self.block = rotated_block

    def drop(self):
        if not (self.game_over or self.paused):
            self.block_y += 1
            if check_collision(self.board, self.block, (self.block_x, self.block_y)):
                self.board = join_block(self.board, self.block, (self.block_x, self.block_y))
                self.new_block()
                self.board, bonus = destroy_filed_lines(self.board)
                self.add_score(bonus)
            self.add_score(1)

    def add_score(self, score_to_add):
        self.score += score_to_add
        self.level = (self.score // 1000) + 1
        pygame.time.set_timer(drop_event, 1000 // self.level)
        print(self.score, self.level)

    def render(self, board, coords):
        block_x, block_y = coords
        for y, row in enumerate(board):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(
                        self.screen,
                        colors[val],
                        pygame.Rect((block_x + x) * cell_size, (block_y + y) * cell_size,
                                    cell_size, cell_size), 0)

    def new_game(self):
        if self.game_over:
            self.board = create_board()
            self.new_block()
            self.level = 1
            self.score = 0
            self.lines = 0
            self.game_over = False

    def set_pause(self):
        self.paused = not self.paused
        print(f'Pause state: {self.paused}')

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.screen.fill((0, 0, 0))
            pygame.draw.line(self.screen,
                             (255, 255, 255),
                             (self.rlim + 1, 0),
                             (self.rlim + 1, self.height - 1))

            self.render(self.board, (0, 0))
            self.render(self.block, (self.block_x, self.block_y))
            self.render(self.next_block, (cols + 1, 2))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                    quit_game()
                elif event.type == drop_event and not self.game_over:
                    self.drop()
                elif event.type == pygame.KEYDOWN and not self.game_over:
                    if event.key == pygame.K_UP:
                        self.rotate()
                    if event.key == pygame.K_LEFT:
                        self.move_block(-1)
                    if event.key == pygame.K_RIGHT:
                        self.move_block(+1)
                    if event.key == pygame.K_DOWN:
                        self.drop()
                    if event.key == pygame.K_ESCAPE:
                        quit_game()
                    if event.key == pygame.K_SPACE:
                        self.set_pause()
            clock.tick(FPS)


if __name__ == '__main__':
    Game = Tetris()
    Game.run()
