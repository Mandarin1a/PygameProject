import os
import sys
import random
import pygame

pygame.init()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f'Файл с изображением {fullname} не найден')
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return level_map


wals_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit()


def coll_test(rect, tiles):
    global DEATH
    global IS_KEY
    hit_list = []
    for tile in tiles:
        a = tiles.index(tile)
        if rect.colliderect(tile):
            if death_block[a] == '3':
                IS_KEY = True
            else:
                hit_list.append(tile)
            if death_block[a] == '2':
                DEATH = True
    return hit_list


def move(rect, movement, tiles):
    coll_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = coll_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            coll_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            coll_types['right'] = True
    rect.y += movement[1]
    hit_list = coll_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            coll_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            coll_types['top'] = True
    return rect, coll_types




game_map = load_level('game_map.txt')
pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption('Jumper')
size = WIDTH, HEIGHT = (1280, 960)
display = pygame.display.set_mode(size, 0, 16)
screen = pygame.Surface((640, 480))
MAP_NUMBER = 0
MAP_LIST = ["gam_map.txt", "game_map2.txt", "game_map3.txt", "game_map4.txt", "game_map5.txt"]
label = pygame.font.SysFont('arial', 36)
game_over = label.render('Game Over', False, (230, 230, 230))
start = label.render('Добро Пожаловать', False, (200, 230, 255))
end = label.render("Спасибо за прохождение", False, (200, 230, 255))
label = pygame.font.SysFont('arial', 24)
game_resert = label.render('Press SPACE to restart', False, (150, 150, 150))
stone = load_image('dirt.png')
grass = load_image('fgrass.png')
spike = load_image('spike.png')
key = load_image('key.png')
bg = load_image("bg.png")
rspike = load_image('rspike.png')
rights = load_image('rights.png')
lefts = load_image('lefts.png')
TILE_SIZE = stone.get_width()
moving_r = False
gameplay = False
DEATH = False
END_GAME = False
START_SCREEN = True
IS_KEY = False
NEXT_LVL = False
moving_l = False

player = load_image('player.png')
player_rect = pygame.Rect(60, 350, player.get_width(), player.get_height())
air_timer = 0
player_y_momentum = 0

while True:
    if START_SCREEN:
        screen.fill(pygame.Color(30, 30, 90))
        screen.blit(start, (180, 180))

    elif END_GAME:
        screen.fill(pygame.Color(30, 30, 90))
        screen.blit(end, (120, 180))

    elif gameplay:

        screen.fill(pygame.Color(150, 200, 250))
        screen.blit(bg, (0, 0))
        tile_rects = []
        death_block = []

        if player_rect.x > 640 or player_rect.y > 480 or player_rect.x < 0 or player_rect.y < 0:
            if MAP_NUMBER < 4:
                MAP_NUMBER += 1
                game_map = load_level(MAP_LIST[MAP_NUMBER])
                player_rect.x = 60
                player_rect.y = 350
            else:
                END_GAME = True


        y = 0
        for row in game_map:
            x = -3
            for tile in row:
                if tile == '1':
                    screen.blit(stone, (x * 16, y * 16))
                elif tile == '2':
                    screen.blit(grass, (x * 16, y * 16))
                elif tile == '3':
                    screen.blit(spike, (x * 16, y * 16))
                elif tile == '4':
                    screen.blit(rspike, (x * 16, y * 16))
                elif tile == '5':
                    screen.blit(lefts, (x * 16, y * 16))
                elif tile == '6':
                    screen.blit(rights, (x * 16, y * 16))
                elif tile == '7' and not IS_KEY:
                    screen.blit(key, (x * 16, y * 16))
                elif tile == '8' and not IS_KEY:
                    screen.blit(stone, (x * 16, y * 16))
                if tile != '0':
                    if tile != "8" or not IS_KEY:
                        tile_rects.append(pygame.Rect(x * 16, y * 16, 16, 16))
                        if tile == "3" or tile == "4" or tile == "5" or tile == "6":
                            death_block.append('2')
                        elif tile == "7":
                            death_block.append('3')
                        else:
                            death_block.append('1')
                x += 1
            y += 1

        player_movement = [0, 0]
        if moving_l:
            player_movement[0] -= 3
        if moving_r:
            player_movement[0] += 3
        player_movement[1] += player_y_momentum
        player_y_momentum += 0.5
        if player_y_momentum > 6:
            player_y_momentum = 6

        player_rect, collisions = move(player_rect, player_movement, tile_rects)

        if DEATH:
            player_rect.x = 60
            player_rect.y = 350
            gameplay = False
            DEATH = False


        if collisions['bottom']:
            player_y_momentum = 0
            air_timer = 0
        else:
            air_timer += 1

        screen.blit(player, (player_rect.x, player_rect.y))

    elif not START_SCREEN and not gameplay and not END_GAME:
        screen.fill(pygame.Color(10, 10, 10))
        screen.blit(game_over, (240, 180))
        screen.blit(game_resert, (205, 220))
        DEATH = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN and gameplay:
            if event.key == pygame.K_d:
                moving_r = True
            if event.key == pygame.K_a:
                moving_l = True
            if event.key == pygame.K_SPACE:
                if air_timer < 12:
                    player_y_momentum -= 10
        if event.type == pygame.KEYDOWN and not gameplay and not START_SCREEN:
            if event.key == pygame.K_SPACE:
                gameplay = True
        if event.type == pygame.KEYDOWN and not gameplay and START_SCREEN:
            gameplay = True
            START_SCREEN = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                moving_r = False
            if event.key == pygame.K_a:
                moving_l = False
    surf = pygame.transform.scale(screen, size)
    display.blit(surf, (0, 0))
    clock.tick(80)
    pygame.display.flip()
