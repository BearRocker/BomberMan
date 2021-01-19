import pygame
from pygame import *
import pyganim
import os
import sys
import random

MAIN_WIDTH = 800  # Ширина создаваемого окна
MAIN_HEIGHT = 900  # Высота
DISPLAY = (MAIN_WIDTH, MAIN_HEIGHT)  # Группируем ширину и высоту в одну переменную
FPS = 60
screen = pygame.display.set_mode(DISPLAY)

BACKGROUND_COLOR = "#004400"
clock = pygame.time.Clock()
PLATFORM_WIDTH = 64
PLATFORM_HEIGHT = 64
PLATFORM_COLOR = "#FF6262"


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

    fon = pygame.transform.scale(load_image('fon.png'), (MAIN_WIDTH, MAIN_HEIGHT))
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


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image = load_image('wall.png')
        self.rect = pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)

    def check(self, booms):
        pass


def load_level(filename):
    filename = "levels/" + filename + '.txt'
    # читаем уровень, убирая символы перевода строки
    print(filename)
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


MOVE_SPEED = 5
WIDTH = 40
HEIGHT = 40
COLOR = "#888888"

ANIMATION_DELAY = 0.1  # скорость смены кадров

ANIMATION_RIGHT = [('pictures/bomberman_right.png', 1)]
ANIMATION_LEFT = [('pictures/bomberman_left.png', 1)]
ANIMATION_UP = [('pictures/bomberman_up.png', 1)]
ANIMATION_DOWN = [('pictures/bomberman_down.png', 1)]
ANIMATION_BOMB = [('pictures/bomb.png', 1)]
ANIMATION_BOMB_BIG = [('pictures/bomb_big.png', 1)]


class Player(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.xvel = 0  # скорость перемещения. 0 - стоять на месте
        self.startX = x  # Начальная позиция Х, пригодится когда будем переигрывать уровень
        self.startY = y
        self.yvel = 0  # скорость вертикального перемещения
        self.image = Surface((WIDTH, HEIGHT))
        self.image.fill(Color(COLOR))
        self.rect = pygame.Rect(x, y, WIDTH, HEIGHT)  # прямоугольный объект
        self.image.set_colorkey(Color(COLOR))  # делаем фон прозрачным
        self.boltAnimRight = pyganim.PygAnimation(ANIMATION_RIGHT)
        self.boltAnimRight.play()
        # Анимация движения влево
        self.boltAnimLeft = pyganim.PygAnimation(ANIMATION_LEFT)
        self.boltAnimLeft.play()
        self.boltAnimStay = pyganim.PygAnimation(ANIMATION_DOWN)
        self.boltAnimStay.play()
        self.boltAnimStay.blit(self.image, (0, 0))  # По-умолчанию, стоим

        self.boltAnimUp = pyganim.PygAnimation(ANIMATION_UP)
        self.boltAnimUp.play()

    def update(self, left, right, up, down, platforms, enemies, tp):
        if up:
            self.image.fill(Color(COLOR))
            self.yvel = -MOVE_SPEED
            self.boltAnimUp.blit(self.image, (0, 0))
            self.boltAnimStay = pyganim.PygAnimation(ANIMATION_UP)
            self.boltAnimStay.play()
        if down:
            self.yvel = MOVE_SPEED
            self.image.fill(Color(COLOR))
            self.boltAnimStay.blit(self.image, (0, 0))
            self.boltAnimStay = pyganim.PygAnimation(ANIMATION_DOWN)
            self.boltAnimStay.play()
        if left:
            self.xvel = -MOVE_SPEED  # Лево = x - n
            self.image.fill(Color(COLOR))
            if up:
                self.boltAnimLeft.blit(self.image, (0, 0))
            else:
                self.boltAnimLeft.blit(self.image, (0, 0))
            self.boltAnimStay = pyganim.PygAnimation(ANIMATION_LEFT)
            self.boltAnimStay.play()
        if right:
            self.xvel = MOVE_SPEED  # Право = x + n
            self.image.fill(Color(COLOR))
            if up:
                self.boltAnimRight.blit(self.image, (0, 0))
            else:
                self.boltAnimRight.blit(self.image, (0, 0))
            self.boltAnimStay = pyganim.PygAnimation(ANIMATION_RIGHT)
            self.boltAnimStay.play()
        if not (left or right):  # стоим, когда нет указаний идти
            self.xvel = 0
            if not up:
                self.image.fill(Color(COLOR))
                self.boltAnimStay.blit(self.image, (0, 0))
        if not (up or down):
            self.yvel = 0
        self.rect.y += self.yvel
        self.collide(0, self.yvel, platforms, enemies, tp)

        self.rect.x += self.xvel  # переносим свои положение на xvel
        self.collide(self.xvel, 0, platforms, enemies, tp)

    def collide(self, xvel, yvel, platforms, enemies, tp):
        for p in platforms:
            if sprite.collide_rect(self, p):  # если есть пересечение стены с игроком
                if xvel > 0:  # если движется вправо
                    self.rect.right = p.rect.left  # то не движется вправо

                if xvel < 0:  # если движется влево
                    self.rect.left = p.rect.right  # то не движется влево

                if yvel > 0:  # если падает вниз
                    self.rect.bottom = p.rect.top  # то не движется вниз
                    self.yvel = 0

                if yvel < 0:  # если движется вверх
                    self.rect.top = p.rect.bottom  # то не движется вверх
                    self.yvel = 0

        for e in enemies:
            if sprite.collide_rect(self, e):
                terminate()

        for t in tp:
            if sprite.collide_rect(self, t):
                main('level2')

    def check(self, booms):
        for boom in booms:
            boom = boom[0]
            if sprite.collide_rect(self, boom):
                print('Вы проиграли')

    def get_coords(self):
        return self.rect.x, self.rect.y


class Destroyable_wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image = load_image('break_wall.png')
        self.rect = pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)

    def check(self, booms):
        for boom in booms:
            boom = boom[0]
            if sprite.collide_rect(self, boom):
                self.kill()
                return self


class Bomb(pygame.sprite.Sprite):
    def __init__(self, coords):
        sprite.Sprite.__init__(self)
        self.image = Surface((WIDTH, HEIGHT))
        self.image.fill(Color(COLOR))
        self.image.set_colorkey(Color(COLOR))  # делаем фон прозрачным
        self.boltAnimBomb = pyganim.PygAnimation(ANIMATION_BOMB)
        self.boltAnimBomb.play()  # Анимация  бомбы
        self.boltAnimBomb_Big = pyganim.PygAnimation(ANIMATION_BOMB_BIG)
        self.boltAnimBomb_Big.play()
        self.boltAnimBomb.blit(self.image, (0, 0))  # По-умолчанию, стоим
        self.rect = pygame.Rect(coords[0] // 64 * 64 + 10, coords[1] // 64 * 64 + 10, PLATFORM_WIDTH, PLATFORM_HEIGHT)

    def animation(self, time):
        self.image.fill(Color(COLOR))
        if time % 2:
            self.boltAnimBomb.blit(self.image, (0, 0))
        else:
            self.boltAnimBomb_Big.blit(self.image, (0, 0))

    def coords(self):
        return self.rect.x, self.rect.y


class Camera:
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = pygame.Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


class BOOM(pygame.sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image = load_image('boom2.png')
        self.rect = pygame.Rect(x - 10, y - 10, PLATFORM_WIDTH, PLATFORM_HEIGHT)


ENEMY_WIDTH = 50
ENEMY_HEIGHT = 50
ENEMY_MOVE_SPEED = 3


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image = load_image('e_1_down.png')
        self.rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)
        self.move = ['left', 'right', 'up', 'down']
        self.yvel = 0
        self.xvel = 0
        self.side, self.len_move = self.choose_side()

    def update(self, level, platforms, bombs, booms):
        if self.side == 'left':
            self.xvel = -ENEMY_MOVE_SPEED
        if self.side == 'right':
            self.xvel = ENEMY_MOVE_SPEED
        if self.side == 'down':
            self.yvel = ENEMY_MOVE_SPEED
        if self.side == 'up':
            self.yvel = -ENEMY_MOVE_SPEED

        self.len_move -= 3

        self.rect.y += self.yvel
        self.collide(0, self.yvel, platforms, bombs, booms)

        self.rect.x += self.xvel
        self.collide(self.xvel, 0, platforms, bombs, booms)

    def collide(self, xvel, yvel, platforms, bombs, booms):
        if self.len_move > 0:
            for p in platforms:
                if sprite.collide_rect(self, p):  # если есть пересечение стены с мобом
                    if xvel > 0:  # если движется вправо
                        self.rect.right = p.rect.left  # то не движется вправо
                        self.side, self.len_move = self.choose_side()

                    if xvel < 0:  # если движется влево
                        self.rect.left = p.rect.right  # то не движется влево
                        self.side, self.len_move = self.choose_side()

                    if yvel > 0:  # если падает вниз
                        self.rect.bottom = p.rect.top  # то не движется вниз
                        self.side, self.len_move = self.choose_side()
                        self.yvel = 0

                    if yvel < 0:  # если движется вверх
                        self.rect.top = p.rect.bottom  # то не движется вверх
                        self.side, self.len_move = self.choose_side()
                        self.yvel = 0
            for b in bombs:
                b = b[0]
                if sprite.collide_rect(self, b):  # если есть пересечение бомбы с мобом
                    if xvel > 0:  # если движется вправо
                        self.rect.right = b.rect.left  # то не движется вправо
                        self.side, self.len_move = self.choose_side()

                    if xvel < 0:
                        self.rect.left = b.rect.right  # то не движется влево
                        self.side, self.len_move = self.choose_side()

                    if yvel > 0:  # если падает вниз
                        self.rect.bottom = b.rect.top  # то не движется вниз
                        self.side, self.len_move = self.choose_side()
                        self.yvel = 0

                    if yvel < 0:  # если движется вверх
                        self.rect.top = b.rect.bottom  # то не движется вверх
                        self.side, self.len_move = self.choose_side()
                        self.yvel = 0
            for boom in booms:
                boom = boom[0]
                if sprite.collide_rect(self, boom):
                   self.kill()
        else:
            self.side, self.len_move = self.choose_side()

    def choose_side(self):
        return random.choice(self.move), random.randint(5 * PLATFORM_WIDTH, 10 * PLATFORM_WIDTH)


class Teleport(pygame.sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image = load_image('door.png')
        self.rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)


def generate_destroyable_walls(level):
    coords_of_walls = []
    for i in range(random.randint(10, 50)):
        y = random.randint(0, len(level) - 1)
        x = random.randint(0, len(level[y]) - 1)
        while (x, y) in coords_of_walls:
            y = random.randint(0, len(level) - 1)
            x = random.randint(0, len(level[y]) - 1)
        if level[y][x] == '.':
            if (x, y) not in [(1, 1), (1, 2), (2, 1)]:
                level[y][x] = '%'
                coords_of_walls.append((x, y))


def generate_teleport(level):
    y = random.randint(0, len(level) - 1)
    x = random.randint(0, len(level[y]) - 1)
    while level[y][x] != '.':
        y = random.randint(0, len(level) - 1)
        x = random.randint(0, len(level[y]) - 1)
    if (x, y) not in [(1, 1), (1, 2), (2, 1)]:
        level[y][x] = '/'


def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + MAIN_WIDTH / 2, -t + MAIN_HEIGHT / 2
    l = min(0, l)  # Не движемся дальше левой границы
    l = max(-(camera.width - MAIN_WIDTH), l)  # Не движемся дальше правой границы
    t = max(-(camera.height - MAIN_HEIGHT), t)  # Не движемся дальше нижней границы
    t = min(0, t)  # Не движемся дальше верхней границы
    # print(l, t, w, h)
    return pygame.Rect(l, t, w, h)


def main(level_to_load='map'):
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()  # Инициация PyGame, обязательная строчка
    pygame.display.set_caption("BomberMan")  # Пишем в шапку
    start_screen()
    pygame.mixer.music.load(os.path.join('pictures', 'background.mp3'))
    pygame.mixer.music.set_volume(0.02)
    pygame.mixer.music.play(-1)
    bg = Surface((MAIN_WIDTH, MAIN_HEIGHT))  # Создание видимой поверхности
    # будем использовать как фон
    bg.fill(Color(BACKGROUND_COLOR))  # Заливаем поверхность сплошным цветом
    bomb_group = pygame.sprite.Group()
    boom_group = pygame.sprite.Group()
    boom_lst = []
    bomb_lst = []
    hero = Player(70, 70)  # создаем героя по (x,y) координатам
    up = down = left = right = False  # по умолчанию - стоим
    level = load_level(level_to_load)
    counter, text = 300, 'TIME 300'.rjust(3)
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    running = True
    all_sprites = pygame.sprite.Group()  # Все объекты
    platforms = []  # то, во что мы будем врезаться или опираться
    enemies = pygame.sprite.Group()
    enem = []
    all_sprites.add(hero)
    generate_destroyable_walls(level)
    generate_teleport(level)
    tp = pygame.sprite.Group()
    on_next_level = []
    x = y = 0  # координаты
    for row in level:  # вся строка
        for col in row:  # каждый символ
            if col == '#':
                platform = Wall(x, y)
                all_sprites.add(platform)
                platforms.append(platform)
            if col == '%':
                wall = Destroyable_wall(x, y)
                all_sprites.add(wall)
                platforms.append(wall)
            if col == '*':
                enemy = Enemy(x, y)
                enemies.add(enemy)
                enem.append(enemy)
            if col == '/':
                teleport = Teleport(x, y)
                tp.add(teleport)
                on_next_level.append(teleport)
            x += PLATFORM_WIDTH  # блоки платформы ставятся на ширине блоков
        y += PLATFORM_HEIGHT  # то же самое и с высотой
        x = 0  # на каждой новой строчке начинаем с нуля
    total_level_width = len(level[0]) * PLATFORM_WIDTH  # Высчитываем фактическую ширину уровня
    total_level_height = len(level) * PLATFORM_HEIGHT  # высоту
    font = pygame.font.SysFont('Consolas', 30)
    camera = Camera(camera_configure, total_level_width, total_level_height)
    boom = pygame.mixer.Sound(os.path.join('pictures', 'bang.wav'))
    boom.set_volume(0.05)
    radius = 2
    while running:  # Основной цикл программы
        screen.blit(bg, (0, 0))  # Каждую итерацию необходимо всё перерисовывать
        for event in pygame.event.get():  # Обрабатываем события
            if event.type == pygame.USEREVENT:
                counter -= 1
                text = f'TIME {str(counter).rjust(3)}'
                bomb_lst_check = []
                boom_draw_check = []
                for timer in range(len(bomb_lst)):
                    if bomb_lst[timer][1]:
                        bomb_lst[timer] = [bomb_lst[timer][0], bomb_lst[timer][1] - 1]
                        bomb_lst_check.append(bomb_lst[timer])
                        for b in bomb_group:
                            b.animation(bomb_lst[timer][1])
                    else:
                        x, y = bomb_lst[timer][0].coords()
                        for rad in range(1, radius + 1):
                            for coords in [(0, 0, 0, 0), (-64, 0, -1, 0), (64, 0, 1, 0), (0, -64, 0, -1), (0, 64, 0, 1)]:
                                try:
                                    if level[y // 64 + coords[3]][x // 64 + coords[2]] != '#' and \
                                            level[y // 64 + coords[3]][x // 64 + coords[2]] != '/' and (y // 64 + coords[3], x // 64 + coords[2]) not in boom_draw_check:
                                        if level[y // 64 + coords[3]][x // 64 + coords[2]] == '%':
                                            boom_draw_check.append((y // 64 + coords[3], x // 64 + coords[2]))
                                        boom_draw = BOOM(x + coords[0] * rad, y + coords[1] * rad)
                                        boom_group.add(boom_draw)
                                        boom_lst.append((boom_draw, 2))
                                except Exception:
                                    pass
                        boom.play()
                boom_lst_check = []
                for timer in range(len(boom_lst)):
                    if boom_lst[timer][1]:
                        boom_lst[timer] = [boom_lst[timer][0], boom_lst[timer][1] - 1]
                        boom_lst_check.append(boom_lst[timer])
                boom_lst = boom_lst_check[::]
                bomb_lst = bomb_lst_check[::]
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                up = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                left = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                right = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                down = True
            elif event.type == pygame.KEYUP and event.key == pygame.K_UP:
                up = False
            elif event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
                left = False
            elif event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
                right = False
            elif event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
                down = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bomb = Bomb(hero.get_coords())
                bomb_group.add(bomb)
                bomb_lst.append((bomb, 3))
        screen.blit(font.render(text, True, (0, 0, 0)), (50, 850))
        camera.update(hero)  # центризируем камеру относительно персонажа
        hero.update(left, right, up, down, platforms, enemies, tp)  # передвижение
        for sprite in bomb_lst:
            screen.blit(sprite[0].image, camera.apply(sprite[0]))
        for sprite in boom_lst:
            screen.blit(sprite[0].image, camera.apply(sprite[0]))
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))
            sprite.check(boom_lst)
            try:
                platforms.remove(sprite.check(boom_lst))
            except Exception:
                pass
        for sprite in enemies:
            screen.blit(sprite.image, camera.apply(sprite))
            sprite.update(level, platforms, bomb_lst, boom_lst)
        for sprite in on_next_level:
            screen.blit(sprite.image, camera.apply(sprite))
        pygame.display.update()  # обновление и вывод всех изменений на экран
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
