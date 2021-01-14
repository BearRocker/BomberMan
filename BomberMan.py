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
ICON_DIR = os.path.dirname(__file__)  # Полный путь к каталогу с файлами


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

    fon = pygame.transform.scale(load_image('grass.png'), (MAIN_WIDTH, MAIN_HEIGHT))
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


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image = load_image('wall.png')
        self.rect = pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)


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


MOVE_SPEED = 5
WIDTH = 40
HEIGHT = 40
COLOR = "#888888"

ANIMATION_DELAY = 0.1  # скорость смены кадров

ANIMATION_RIGHT = [('pictures/bomberman_right.png', 1)]
ANIMATION_LEFT = [('pictures/bomberman_left.png', 1)]
ANIMATION_UP = [('pictures/bomberman_up.png', 1)]
ANIMATION_DOWN = [('pictures/bomberman_down.png', 1)]


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

    def update(self, left, right, up, down, platforms, enemies):
        if up:
            self.image.fill(Color(COLOR))
            self.yvel = -MOVE_SPEED
            self.boltAnimUp.blit(self.image, (0, 0))
        if down:
            self.yvel = MOVE_SPEED
            self.image.fill(Color(COLOR))
            self.boltAnimStay.blit(self.image, (0, 0))
        if left:
            self.xvel = -MOVE_SPEED  # Лево = x- n
            self.image.fill(Color(COLOR))
            if up:
                self.boltAnimLeft.blit(self.image, (0, 0))
            else:
                self.boltAnimLeft.blit(self.image, (0, 0))
        if right:
            self.xvel = MOVE_SPEED  # Право = x + n
            self.image.fill(Color(COLOR))
            if up:
                self.boltAnimRight.blit(self.image, (0, 0))
            else:
                self.boltAnimRight.blit(self.image, (0, 0))
        if not (left or right):  # стоим, когда нет указаний идти
            self.xvel = 0
            if not up:
                self.image.fill(Color(COLOR))
                self.boltAnimStay.blit(self.image, (0, 0))
        if not (up or down):
            self.yvel = 0
        self.rect.y += self.yvel
        self.collide(0, self.yvel, platforms, enemies)

        self.rect.x += self.xvel  # переносим свои положение на xvel
        self.collide(self.xvel, 0, platforms, enemies)

    def collide(self, xvel, yvel, platforms, enemies):
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

    def get_coords(self):
        return self.rect.x, self.rect.y


class Bomb(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image = load_image('bomb.png')

    def draw(self, coords):
        self.rect = pygame.Rect(coords[0], coords[1], PLATFORM_WIDTH, PLATFORM_HEIGHT)
        print('+')


class Camera:
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = pygame.Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


class Destroyable_wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image = load_image('break_wall.png')
        self.rect = pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)


ENEMY_WIDTH = 60
ENEMY_HEIGHT = 60
ENEMY_MOVE_SPEED = 3


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image = load_image('bomberman.png')
        self.rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)
        self.move = ['left', 'right', 'up', 'down']
        self.yvel = 0
        self.xvel = 0
        self.side, self.len_move = self.choose_side()

    def update(self, level, platforms):
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
        self.collide(0, self.yvel, platforms)

        self.rect.x += self.xvel  # переносим свои положение на xvel
        self.collide(self.xvel, 0, platforms)

    def collide(self, xvel, yvel, platforms):
        if self.len_move > 0:
            for p in platforms:
                if sprite.collide_rect(self, p):  # если есть пересечение стены с игроком
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
        else:
            self.side, self.len_move = self.choose_side()

    def choose_side(self):
        return random.choice(self.move), random.randint(5 * PLATFORM_WIDTH, 10 * PLATFORM_WIDTH)


def generate_destroyable_walls(level):
    coords_of_walls = []
    for i in range(random.randint(100, 200)):
        y = random.randint(0, len(level) - 1)
        x = random.randint(0, len(level[y]) - 1)
        while (x, y) in coords_of_walls:
            y = random.randint(0, len(level) - 1)
            x = random.randint(0, len(level[y]) - 1)
        if level[y][x] == '.':
            if (x, y) not in [(1, 1), (1, 2), (2, 1)]:
                level[y][x] = '%'
                coords_of_walls.append((x, y))


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


def main():
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
    bomb = Bomb(bomb_group)
    hero = Player(70, 70)  # создаем героя по (x,y) координатам
    up = down = left = right = False  # по умолчанию - стоим
    level = load_level('map')
    counter, text = 300, 'TIME 300'.rjust(3)
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    running = True
    all_sprites = pygame.sprite.Group()  # Все объекты
    platforms = []  # то, во что мы будем врезаться или опираться
    enemies = pygame.sprite.Group()
    enem = []
    all_sprites.add(hero)
#    generate_destroyable_walls(level)
    x = y = 0  # координаты
    for row in level:  # вся строка
        for col in row:  # каждый символ
            if col == '#':
                platform = Tile(x, y)
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
            x += PLATFORM_WIDTH  # блоки платформы ставятся на ширине блоков
        y += PLATFORM_HEIGHT  # то же самое и с высотой
        x = 0  # на каждой новой строчке начинаем с нуля

    total_level_width = len(level[0]) * PLATFORM_WIDTH  # Высчитываем фактическую ширину уровня
    total_level_height = len(level) * PLATFORM_HEIGHT  # высоту
    font = pygame.font.SysFont('Consolas', 30)
    camera = Camera(camera_configure, total_level_width, total_level_height)
    bomb_check = False
    while running:  # Основной цикл программы
        screen.blit(bg, (0, 0))  # Каждую итерацию необходимо всё перерисовывать
        for event in pygame.event.get():  # Обрабатываем события
            if event.type == pygame.USEREVENT:
                counter -= 1
                text = f'TIME {str(counter).rjust(3)}'
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
                Bomb.draw(bomb, hero.get_coords())
                bomb_check = True
        screen.blit(font.render(text, True, (0, 0, 0)), (50, 850))
        camera.update(hero)  # центризируем камеру относительно персонажа
        hero.update(left, right, up, down, platforms, enemies)  # передвижение
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))
        if bomb_check:
            for sprite in bomb_group:
                screen.blit(sprite.image, camera.apply(sprite))
        for sprite in enemies:
            screen.blit(sprite.image, camera.apply(sprite))
            sprite.update(level, platforms)
        pygame.display.update()  # обновление и вывод всех изменений на экран
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
