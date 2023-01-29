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
    'tetris_cyan.png',  # blue
    'tetris_blue.png',  # dark blue
    'tetris_green.png',  # green
    'tetris_yellow.png',  # yellow
    'tetris_red.png',  # red
    'tetris_purple.png'  # purple
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
    return new_board, bonus_points, cleared_lines


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


def create_db():
    con = sqlite3.connect('C:/ProgramData/results.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE results (
    ID    INTEGER PRIMARY KEY AUTOINCREMENT
                  UNIQUE
                  NOT NULL,
    Name  STRING,
    Score INTEGER NOT NULL,
    Time  STRING);
    ''')


def get_best_res():
    con = sqlite3.connect('C:/ProgramData/results.db')
    cur = con.cursor()
    best = cur.execute('''
    SELECT Score FROM results
    ORDER BY Score DESC
    ''').fetchone()
    if best:
        return best[0]
    else:
        return 0


def add_res_to_db(result):
    if not os.path.exists('C:/ProgramData/results.db'):
        create_db()
    name = os.getlogin()
    if name:
        game_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        con = sqlite3.connect('C:/ProgramData/results.db')
        cur = con.cursor()
        cur.execute(f'INSERT INTO results (Name, Score, Time) VALUES (?, ?, ?)',
                    (name, result, game_time))
        con.commit()
        return True
    return False


def print_leaderboard(new_res_saved):
    con = sqlite3.connect('C:/ProgramData/results.db')
    cur = con.cursor()
    results = cur.execute('''SELECT Name, Score, Time FROM results
                             ORDER BY Score DESC''').fetchall()
    last_result = cur.execute('''SELECT Name, Score, Time FROM results
                             ORDER BY ID DESC''').fetchone()
    s = []
    for index, res in enumerate(results):
        if index >= 10:
            break
        s.append(f'{index + 1})\t{res[0]}{" " * (15 - len(res[0]))}{res[1]}'
              f'{" " * (10 - len(str(res[1])))}{res[2]}')
    place = results.index(last_result) + 1
    return s, place


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Tetris:
    def __init__(self):
        pygame.init()
        self.width = cell_size * (cols + 10)
        self.height = cell_size * (rows + 3) - 14
        self.rlim = cell_size * cols
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.next_block = choice(blocks)
        self.board = create_board()
        self.new_block()
        self.level = 1
        self.score = 0
        self.lines = 0
        self.best_score = get_best_res()

        self.game_over = False
        self.paused = False
        self.on_but_1 = False
        self.on_but_2 = False

        pygame.mixer.music.load("data/tetris_music.mp3")
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)

        self.start_screen()
        self.draw()

        pygame.time.set_timer(drop_event, 1000 // self.level)
        pygame.key.set_repeat(250, 25)

    def start_screen(self):
        font = pygame.font.Font('data/BarcadeBrawlRegular.ttf', 40)
        tetris = font.render("TETRIS", True, (0, 255, 255))
        tetris_x = self.width // 2 - tetris.get_width() // 2
        tetris_y = 20
        self.screen.blit(tetris, (tetris_x, tetris_y))

        start_x = self.width // 2 - 200 // 2
        start_y = self.height // 2 - 45
        pygame.draw.rect(self.screen, but_color_light,
                         ((start_x, start_y), (200, 40)), width=0)

        quit_x = self.width // 2 - 200 // 2
        quit_y = self.height // 2 + 5
        pygame.draw.rect(self.screen, but_color_light,
                         ((quit_x, quit_y), (200, 40)), width=0)
        font2 = pygame.font.Font('data/BarcadeBrawlRegular.ttf', 7)
        by = font2.render("By Alexandr Zolotarev and Aleksandra Druk", True, (0, 255, 255))
        by_x = self.width // 2 - by.get_width() // 2
        by_y = self.height - 20
        self.screen.blit(by, (by_x, by_y))

        font3 = pygame.font.Font('data/BarcadeBrawlRegular.ttf', 15)
        start_text = font3.render("Start", True, (0, 0, 0))
        start_text_x = start_x + 100 - start_text.get_width() // 2
        start_text_y = start_y + 20 - start_text.get_height() // 2
        self.screen.blit(start_text, (start_text_x, start_text_y))

        quit_text = font3.render("quit", True, (0, 0, 0))
        quit_text_x = quit_x + 100 - quit_text.get_width() // 2
        quit_text_y = quit_y + 20 - quit_text.get_height() // 2
        self.screen.blit(quit_text, (quit_text_x, quit_text_y))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    return  # начинаем игру
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse = pygame.mouse.get_pos()
                    if start_x <= mouse[0] <= start_x + 200 and \
                            start_y <= mouse[1] <= start_y + 40:
                        return
                    elif quit_x <= mouse[0] <= quit_x + 200 and \
                            quit_y <= mouse[1] <= quit_y + 40:
                        pygame.quit()
                        sys.exit()
            pygame.display.flip()

    def game_over_screen(self, last):
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font('data/BarcadeBrawlRegular.ttf', 30)
        game_over = font.render("Game over!", True, (0, 255, 255))
        over_x = self.width // 2 - game_over.get_width() // 2
        over_y = 20
        self.screen.blit(game_over, (over_x, over_y))

        top10, place = print_leaderboard(last)
        intro_text = ["Leaderboard top 10:"] + top10

        font = pygame.font.Font('data/UbuntuMono-R.ttf', 13)
        text_coord = 53
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 5
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            self.screen.blit(string_rendered, intro_rect)

        font = pygame.font.Font('data/BarcadeBrawlRegular.ttf', 15)
        your_place = font.render(f"Your place: {place}", True, (0, 255, 255))
        place_x = 10
        place_y = text_coord + 25
        self.screen.blit(your_place, (place_x, place_y))

        start_x = self.width // 2 - 200 // 2
        start_y = self.height - 90
        pygame.draw.rect(self.screen, but_color_light,
                         ((start_x, start_y), (200, 35)), width=0)

        quit_x = self.width // 2 - 200 // 2
        quit_y = self.height - 45
        pygame.draw.rect(self.screen, but_color_light,
                         ((quit_x, quit_y), (200, 35)), width=0)

        font3 = pygame.font.Font('data/BarcadeBrawlRegular.ttf', 15)
        start_text = font3.render("new game", True, (0, 0, 0))
        start_text_x = start_x + 100 - start_text.get_width() // 2
        start_text_y = start_y + 20 - start_text.get_height() // 2
        self.screen.blit(start_text, (start_text_x, start_text_y))

        quit_text = font3.render("quit", True, (0, 0, 0))
        quit_text_x = quit_x + 100 - quit_text.get_width() // 2
        quit_text_y = quit_y + 20 - quit_text.get_height() // 2
        self.screen.blit(quit_text, (quit_text_x, quit_text_y))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse = pygame.mouse.get_pos()
                    if start_x <= mouse[0] <= start_x + 200 and \
                            start_y <= mouse[1] <= start_y + 40:
                        self.new_game()
                        return
                    elif quit_x <= mouse[0] <= quit_x + 200 and \
                            quit_y <= mouse[1] <= quit_y + 40:
                        pygame.quit()
                        sys.exit()

            pygame.display.flip()


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
                self.board, bonus, lines = destroy_filed_lines(self.board)
                self.add_score(bonus)
                self.lines += lines
            self.add_score(1)

    def add_score(self, score_to_add):
        self.score += score_to_add
        self.level = (self.score // 1000) + 1
        pygame.time.set_timer(drop_event, 1000 // self.level)

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
        result_added = add_res_to_db(self.score)
        self.game_over_screen(result_added)


    def new_game(self):
        if self.game_over:
            self.board = create_board()
            self.new_block()
            self.level = 1
            self.score = 0
            self.lines = 0
            self.best_score = get_best_res()
            self.game_over = False
            self.paused = False

    def set_pause(self):
        self.paused = not self.paused
        print(f'Pause state: {self.paused}')

    def draw(self):
        pygame.draw.line(self.screen, (255, 255, 255),
                         (cell_size * cols + 1, 0),
                         (cell_size * cols + 1, cell_size * rows + 1))
        pygame.draw.line(self.screen, (255, 255, 255),
                         (0, cell_size * rows + 1),
                         (cell_size * cols + 1, cell_size * rows + 1))

        if self.on_but_1:
            pygame.draw.rect(self.screen, but_color_dark,
                             ((x_btn1, y_btn1), (w_btn, h_btn)), width=0)
            pygame.draw.rect(self.screen, but_color_light,
                             ((x_btn2, y_btn2), (w_btn, h_btn)), width=0)
        elif self.on_but_2:
            pygame.draw.rect(self.screen, but_color_light,
                             ((x_btn1, y_btn1), (w_btn, h_btn)), width=0)
            pygame.draw.rect(self.screen, but_color_dark,
                             ((x_btn2, y_btn2), (w_btn, h_btn)), width=0)
        else:
            pygame.draw.rect(self.screen, but_color_light,
                             ((x_btn1, y_btn1), (w_btn, h_btn)), width=0)
            pygame.draw.rect(self.screen, but_color_light,
                             ((x_btn2, y_btn2), (w_btn, h_btn)), width=0)
        font = pygame.font.Font('data/BarcadeBrawlRegular.ttf', 10)
        text1 = font.render("New Game", True, (0, 0, 0))
        text1_x = x_btn1 + w_btn // 2 - text1.get_width() // 2
        text1_y = y_btn1 + h_btn // 2 - text1.get_height() // 2

        if not self.paused:
            text2 = font.render("Pause", True, (0, 0, 0))
        else:
            text2 = font.render("Continue", True, (0, 0, 0))
        text2_x = x_btn2 + w_btn // 2 - text2.get_width() // 2
        text2_y = y_btn2 + h_btn // 2 - text2.get_height() // 2
        self.screen.blit(text1, (text1_x, text1_y))
        self.screen.blit(text2, (text2_x, text2_y))

        text_score = font.render(f"Score: {self.score}", True, (255, 255, 255))
        score_x = x_btn2
        score_y = y_btn2 + h_btn + 20
        self.screen.blit(text_score, (score_x, score_y))

        text_level = font.render(f"Level: {self.level}", True, (255, 255, 255))
        level_x = x_btn2
        level_y = y_btn2 + h_btn + 50
        self.screen.blit(text_level, (level_x, level_y))

        text_level = font.render(f"Lines: {self.lines}", True, (255, 255, 255))
        level_x = x_btn2
        level_y = y_btn2 + h_btn + 80
        self.screen.blit(text_level, (level_x, level_y))

        text_level = font.render(f"High Score: {self.best_score}", True, (255, 255, 255))
        level_x = x_btn2
        level_y = y_btn2 + h_btn + 110
        self.screen.blit(text_level, (level_x, level_y))

        font = pygame.font.Font('data/BarcadeBrawlRegular.ttf', 25)
        name = font.render("Tetris", True, (0, 255, 255))
        name_x = 10
        name_y = cell_size * rows + 10
        self.screen.blit(name, (name_x, name_y))

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.screen.fill((0, 0, 0))
            self.draw()

            self.render(self.board, (0, 0))
            self.render(self.block, (self.block_x, self.block_y))
            self.render(self.next_block, (cols + 1, 2))
            pygame.display.set_caption('Tetris')
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
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
                    if x_btn1 <= mouse[0] <= x_btn1 + w_btn and \
                            y_btn1 <= mouse[1] <= y_btn1 + h_btn:
                        self.game_over = True
                        self.new_game()
                    elif x_btn2 <= mouse[0] <= x_btn2 + w_btn and \
                            y_btn2 <= mouse[1] <= y_btn2 + h_btn:
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
