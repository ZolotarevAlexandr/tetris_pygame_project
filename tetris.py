import os
import sqlite3
import sys
from datetime import datetime
from random import choice

import pygame

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
    'tetris_orange.png',  # orange
    'tetris_cyan.png', # blue
    'tetris_blue.png', # dark blue
    'tetris_green.png',  # green
    'tetris_yellow.png', # yellow
    'tetris_red.png',  # red
    'tetris_orange.png'  # purple
)

but_color_light = (0, 255, 255)
but_color_dark = (0, 180, 180)

x_btn1, y_btn1 = 200, 90
x_btn2, y_btn2 = 200, 140
w_btn, h_btn = 140, 35

cell_size = 18
cols = 10
rows = 20
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


def set_new_best(new_best):
    with open('data/best.txt', 'w') as best_res_file:
        best_res_file.write(str(new_best))


def quit_game():
    sys.exit()


def create_db():
    con = sqlite3.connect('C:\ProgramData/results.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE results (
    ID    INTEGER PRIMARY KEY AUTOINCREMENT
                  UNIQUE
                  NOT NULL,
    Name  STRING,
    Score INTEGER NOT NULL,
    Time  STRING);
    ''')


def add_res_to_db(result):
    if not os.path.exists('C:\ProgramData/results.db'):
        create_db()
    name = input('Input your name for leaderboard (leave empty to not save): ')
    if name:
        game_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        con = sqlite3.connect('C:\ProgramData/results.db')
        cur = con.cursor()
        cur.execute(f'INSERT INTO results (Name, Score, Time) VALUES (?, ?, ?)',
                    (name, result, game_time))
        con.commit()
        print('Result writen!')
        return True
    return False


def print_leaderboard(new_res_saved):
    con = sqlite3.connect('C:\ProgramData/results.db')
    cur = con.cursor()
    results = cur.execute('''SELECT * FROM results
                             ORDER BY Score DESC''').fetchall()
    last_result = cur.execute('''SELECT * FROM results
                             ORDER BY ID DESC''').fetchone()
    for index, res in enumerate(results):
        if index >= 10:
            break
        print(f'{index + 1}) {res[0]}\t{res[1]}\t{res[2]}\t{res[3]}')
    if new_res_saved:
        print(f'Your place is: {results.index(last_result) + 1}')


def draw(screen, game):
    if game.on_but_1:
        pygame.draw.t_colorrect(screen, but_color_dark, ((x_btn1, y_btn1), (w_btn, h_btn)), width=0)
        pygame.draw.rect(screen, but_color_light, ((x_btn2, y_btn2), (w_btn, h_btn)), width=0)
    elif game.on_but_2:
        pygame.draw.rect(screen, but_color_light, ((x_btn1, y_btn1), (w_btn, h_btn)), width=0)
        pygame.draw.rect(screen, but_color_dark, ((x_btn2, y_btn2), (w_btn, h_btn)), width=0)
    else:
        pygame.draw.rect(screen, but_color_light, ((x_btn1, y_btn1), (w_btn, h_btn)), width=0)
        pygame.draw.rect(screen, but_color_light, ((x_btn2, y_btn2), (w_btn, h_btn)), width=0)
    font = pygame.font.Font(None, 30)
    text1 = font.render("New Game", True, (0, 0, 0))
    text1_x = x_btn1 + w_btn // 2 - text1.get_width() // 2
    text1_y = y_btn1 + h_btn // 2 - text1.get_height() // 2

    if game.paused == False:
        text2 = font.render("Pause", True, (0, 0, 0))
    else:
        text2 = font.render("Continue", True, (0, 0, 0))
    text2_x = x_btn2 + w_btn // 2 - text2.get_width() // 2
    text2_y = y_btn2 + h_btn // 2 - text2.get_height() // 2
    screen.blit(text1, (text1_x, text1_y))
    screen.blit(text2, (text2_x, text2_y))


    text_score = font.render(f"Score: {game.score}", True, (255, 255, 255))
    score_x = x_btn2 + w_btn + 20
    score_y = y_btn2
    screen.blit(text_score, (score_x, score_y))


def load_image(name, colorkey=None):
    fullname = name
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Tetris:
    def __init__(self):
        pygame.init()
        self.width = cell_size * (cols + 10)
        self.height = cell_size * rows
        self.rlim = cell_size * cols
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.next_block = choice(blocks)
        self.board = create_board()
        self.new_block()
        self.level = 1
        self.score = 0

        try:
            with open('C:\ProgramData/best.txt', 'r') as best_res_file:
                self.best_score = int(best_res_file.readline())
        except FileNotFoundError:
            with open('C:\ProgramData/best.txt', 'w') as best_res_file:
                best_res_file.write('0')
                self.best_score = 0
        self.game_over = False
        self.paused = False
        self.on_but_1 = False
        self.on_but_2 = False

        draw(self.screen, self)

        pygame.time.set_timer(drop_event, 1000 // self.level)
        pygame.key.set_repeat(250, 25)

    def new_block(self):
        self.block = self.next_block[:]
        self.next_block = choice(blocks)
        self.block_x = int(cols / 2 - len(self.block[0]) / 2)
        self.block_y = 0

        if check_collision(self.board, self.block, (self.block_x, self.block_y)):
            self.set_gameover()

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
        all_sprites = pygame.sprite.Group()
        for y, row in enumerate(board):
            for x, val in enumerate(row):
                if val:
                    sprite = pygame.sprite.Sprite()
                    # определим его вид
                    sprite.image = load_image(colors[val])
                    # и размеры
                    sprite.rect = sprite.image.get_rect()
                    # добавим спрайт в группу
                    all_sprites.add(sprite)
                    sprite.rect.x = (block_x + x) * cell_size
                    sprite.rect.y = (block_y + y) * cell_size
        all_sprites.draw(self.screen)

    def set_gameover(self):
        self.game_over = True
        print('Game Over!')

        result_added = add_res_to_db(self.score)
        if self.score > self.best_score:
            self.best_score = self.score
            set_new_best(self.best_score)

        print('Leaderboard top 10:')
        print_leaderboard(result_added)

    def new_game(self):
        if self.game_over:
            self.board = create_board()
            self.new_block()
            self.level = 1
            self.score = 0
            try:
                with open('C:\ProgramData/best.txt', 'r') as best_res_file:
                    self.best_score = int(best_res_file.readline())
            except FileNotFoundError:
                with open('C:\ProgramData/best.txt', 'w') as best_res_file:
                    best_res_file.write('0')
                    self.best_score = 0
            self.game_over = False
            self.paused = False

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
            draw(self.screen, self)

            self.render(self.board, (0, 0))
            self.render(self.block, (self.block_x, self.block_y))
            self.render(self.next_block, (cols + 1, 2))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                    quit_game()
                elif event.type == drop_event and not self.game_over:
                    self.drop()
                elif event.type == pygame.KEYDOWN:
                    if not self.game_over:
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
                    if event.key == pygame.K_r:
                        self.new_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse = pygame.mouse.get_pos()
                    if x_btn1 <= mouse[0] <= x_btn1 + w_btn and y_btn1 <= mouse[1] <= y_btn1 + h_btn:
                        self.game_over = True
                        self.new_game()
                    elif x_btn2 <= mouse[0] <= x_btn2 + w_btn and y_btn2 <= mouse[1] <= y_btn2 + h_btn:
                        self.set_pause()

                mouse = pygame.mouse.get_pos()

                if x_btn1 <= mouse[0] <= x_btn1 + w_btn and y_btn1 <= mouse[1] <= y_btn1 + h_btn:
                    self.on_but_1 = True
                elif x_btn2 <= mouse[0] <= x_btn2 + w_btn and y_btn2 <= mouse[1] <= y_btn2 + h_btn:
                    self.on_but_2 = True
                else:
                    self.on_but_1 = False
                    self.on_but_2 = False
            clock.tick(FPS)


if __name__ == '__main__':
    Game = Tetris()
    Game.run()
