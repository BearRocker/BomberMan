import pygame
import random as rnd
import copy
import os
import sys


FPS = 60
SIZE = WIDTH, HEIGHT = 600, 600

pygame.init()
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('pictures', name)
    try:
        image = pygame.image.load(fullname)
    except AttributeError:
        print('error')
    else:
        if colorkey is not None:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "pictures/" + filename + '.txt'
    # читаем уровень, убирая символы перевода строки
    print(filename)
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


tile_images = {  # Tile names and images
        'wall': load_image('wall.png'),
        'grass': load_image('grass.png')
    }
player_image = load_image('bomberman.png')
tile_width = tile_height = 64
player = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = (pos_x, pos_y)

    def move(self, x, y):
        camera.dx -= tile_width * (x - self.pos[0])
        camera.dy -= tile_height * (y - self.pos[1])
        self.pos = (x, y)
        for sprite in tiles_group:
            camera.apply(sprite)


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('grass', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('grass', x, y)
                new_player = Player(x, y)
                level[y][x] = '.'
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x = obj.abs_pos[0] + self.dx
        obj.rect.y = obj.abs_pos[1] + self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = 0
        self.dy = 0

start_screen()
level_map = load_level('map')

player, level_x, level_y = generate_level(level_map)
camera = Camera()


def move(hero, movement):
    x, y = hero.pos
    if movement == "up":
        if y > 0 and level_map[y - 1][x] == ".":
            hero.move(x, y - 1)
    elif movement == "down":
        if y < level_y - 1 and level_map[y + 1][x] == ".":
            hero.move(x, y + 1)
    elif movement == "left":
        if x > 0 and level_map[y][x - 1] == ".":
            hero.move(x - 1, y)
    elif movement == "right":
        if x < level_x - 1 and level_map[y][x + 1] == ".":
            hero.move(x + 1, y)
    clock.tick(15)


running = True
camera.update(player)
x = ''
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                x = 'up'
            elif event.key == pygame.K_DOWN:
                x = 'down'
            elif event.key == pygame.K_LEFT:
                x = 'left'
            elif event.key == pygame.K_RIGHT:
                x = 'right'
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                x = ''
    move(player, x)
    screen.fill(pygame.Color("white"))
    tiles_group.draw(screen)
    player_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()