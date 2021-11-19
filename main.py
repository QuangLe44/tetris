import pygame
import random

from pygame.locals import *
pygame.font.init()
pygame.mixer.init()
pygame.display.init()

pygame.mixer.music.load("MEGALOVANIA(1).wav")
crash = pygame.mixer.Sound("Crash.wav")
clear = pygame.mixer.Sound("TING SOUND EFFECT.wav")
End = pygame.mixer.Sound("End.wav")
endpic = pygame.image.load("troll.png")
winpic = pygame.image.load("win.jpg")
back = pygame.image.load("Starsinthesky.jpg")
Win = pygame.mixer.Sound("PARTY POPPER with SOUND Green Screen HD.wav")

s_width = 800
s_height = 700
play_width = 300
play_height = 600
block_size = 30


top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height


S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]


class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


def create_grid(locked_pos={}):
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j,i)]
                grid[i][j] = c
    return grid

def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False


def get_shape():
    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("comicsans", size, bold = True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width /2 - (label.get_width()/2), top_left_y + play_height/2 - label.get_height()/2))


def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (128,128,128), (sx, sy + i*block_size), (sx+play_width, sy+ i*block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j*block_size, sy),(sx + j*block_size, sy + play_height))


def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0,0,0) not in row:
            pygame.mixer.Sound.play(clear)
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j,i)]
                except:
                    continue

    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc


def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 40)
    label = font.render('Next Shape', 1, (0,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 30))


def update_score(nscore):
    score = max_score()

    with open('scores.txt', 'w') as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))


def max_score():
    with open('scores.txt', 'r') as f:
        lines = f.readlines()
        score = lines[0].strip()

    return score


def draw_window(surface, grid, score=0, last_score = 0):
    surface.fill((0, 0, 0))
    surface.blit(pygame.transform.scale(back, (s_width, s_height)), (0, 0))

    pygame.font.init()
    font = pygame.font.SysFont('comicsans', 80)
    label = font.render('TETRIS', 1, (150,0,150))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))


    font = pygame.font.SysFont('comicsans', 40)
    label = font.render('Score: ' + str(score), 1, (212,175,55))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100

    surface.blit(label, (sx + 20, sy + 140))

    label = font.render('High Score: ' + last_score, 1, (212,175,55))

    sx = top_left_x - 200
    sy = top_left_y + 200

    surface.blit(label, (sx - 20, sy + 100))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), 0)

    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

    draw_grid(surface, grid)

def main(win):
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.3)

    last_score = max_score()
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5
    level_time = 0
    score = 0
    Round_1 = True
    Round_2 = True
    Round_3 = True

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_time()
        level_time += clock.get_time()
        clock.tick(60)

        if level_time/1000 > 5:
            level_time = 0
            if level_time > 0.12:
                level_time -= 0.005

        if fall_time/1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                pygame.mixer.Sound.play(crash)
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()

        press = pygame.key.get_pressed()
        if press[pygame.K_LEFT]:
            current_piece.x -= press[pygame.K_LEFT]
            pygame.time.delay(100)
            if not (valid_space(current_piece, grid)):
                current_piece.x += 1
        if press[pygame.K_RIGHT]:
            current_piece.x += press[pygame.K_RIGHT]
            pygame.time.delay(100)
            if not (valid_space(current_piece, grid)):
                current_piece.x -= 1
        if press[pygame.K_DOWN]:
            current_piece.y += press[pygame.K_DOWN]
            pygame.time.delay(100)
            if not (valid_space(current_piece, grid)):
                current_piece.y -= 1
        if press[pygame.K_UP]:
            current_piece.rotation += press[pygame.K_UP]
            pygame.time.delay(150)
            if not (valid_space(current_piece, grid)):
                current_piece.rotation -= 1

        if score < 100:
            if Round_1:
                win.fill((0, 0, 0))
                draw_text_middle(win, "ROUND 1", 120, (255, 255, 255))
                pygame.display.update()
                pygame.time.delay(1000)
                Round_1 = False
            fall_speed = 0.5

        elif score >= 100 and score < 200:
            if Round_2:
                win.fill((0, 0, 0))
                draw_text_middle(win, "ROUND 2", 120, (255, 255, 255))
                pygame.display.update()
                pygame.time.delay(1000)
                Round_2 = False
            fall_speed = 0.25

        elif score >= 200 and score < 300:
            if Round_3:
                win.fill((0, 0, 0))
                draw_text_middle(win, "ROUND 3", 120, (255, 255, 255))
                pygame.display.update()
                pygame.time.delay(1000)
                Round_3 = False
            fall_speed = 0.25
            if press[pygame.K_LEFT]:
                current_piece.x += press[pygame.K_LEFT] * 2
                pygame.time.delay(100)
                if not (valid_space(current_piece, grid)):
                    current_piece.x -= 1
            if press[pygame.K_RIGHT]:
                current_piece.x -= press[pygame.K_RIGHT] * 2
                pygame.time.delay(100)
                if not (valid_space(current_piece, grid)):
                    current_piece.x += 1
            if press[pygame.K_DOWN]:
                current_piece.y -= press[pygame.K_DOWN]
                if not (valid_space(current_piece, grid)):
                    current_piece.y += 1
                current_piece.rotation += press[pygame.K_DOWN]
                pygame.time.delay(100)
                if not (valid_space(current_piece, grid)):
                    current_piece.rotation -= 1
            if press[pygame.K_UP]:
                current_piece.rotation -= press[pygame.K_UP]
                if not (valid_space(current_piece, grid)):
                    current_piece.rotation += 1
                current_piece.y += press[pygame.K_UP]
                pygame.time.delay(150)
                if not (valid_space(current_piece, grid)):
                    current_piece.y -= 1

        else:
            pygame.mixer.music.stop()
            pygame.mixer.Sound.play(Win)
            win.fill((0, 0, 0))
            win.blit(pygame.transform.scale(winpic, (s_width, s_height)), (0, 0))
            draw_text_middle(win, "YOU WIN", 120, (205, 0, 0))
            pygame.display.update()
            pygame.time.delay(5000)
            run = False
            update_score(score)


        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10

        draw_window(win, grid, score, last_score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            pygame.mixer.music.stop()
            pygame.mixer.Sound.play(End)
            win.fill((0, 0, 0))
            win.blit(pygame.transform.scale(endpic, (s_width, s_height)), (0, 0))
            draw_text_middle(win, "YOU LOSE", 120, (205,0,0))
            pygame.display.update()
            pygame.time.delay(5000)
            run = False
            update_score(score)

def main_menu(win):
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text_middle(win, 'Press Any Key To Play', 80, (255,255,255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win)

    pygame.display.quit()


win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')
main_menu(win)