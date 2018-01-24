import pygame
from pygame import *
from blocks import *
from monsters import *
from pygame.rect import Rect

import helperspygame  # Преобразует tmx карты в формат  спрайтов pygame
import tmxreader  # Может загружать tmx файлы
from player import *

# Объявляем переменные
WIN_WIDTH = 800  # Ширина создаваемого окна
WIN_HEIGHT = 600  # Высота
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)  # Группируем ширину и высоту в одну переменную
CENTER_OF_SCREEN = WIN_WIDTH / 2, WIN_HEIGHT / 2

FILE_DIR = os.path.dirname(__file__)


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)

    def reverse(self, pos):  # получение внутренних координат из глобальных
        return pos[0] - self.state.left, pos[1] - self.state.top


def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + WIN_WIDTH / 2, -t + WIN_HEIGHT / 2

    l = max(-(camera.width - WIN_WIDTH), min(0, l))
    t = min(0, max(-(camera.height - WIN_HEIGHT), t))

    return Rect(l, t, w, h)


def loadLevel(name):
    world_map = tmxreader.TileMapParser().parse_decode('%s/%s.tmx' % (FILE_DIR, name))  # загружаем карту
    resources = helperspygame.ResourceLoaderPygame()  # инициируем преобразователь карты
    resources.load(world_map)  # и преобразуем карту в понятный pygame формат

    sprite_layers = helperspygame.get_layers_from_map(resources)  # получаем все слои карты

    # берем слои по порядку
    # 0 - слой фона,
    # 1 - слой блоков,
    # 2 - слой смертельных блоков
    # 3 - слой объектов монстров,
    # 4 - слой объектов телепортов
    platforms_layer = sprite_layers[1]
    dieBlocks_layer = sprite_layers[2]

    for row in range(0, platforms_layer.num_tiles_x):  # перебираем все координаты тайлов
        for col in range(0, platforms_layer.num_tiles_y):
            if platforms_layer.content2D[col][row]:
                pf = Platform(row * PLATFORM_WIDTH, col * PLATFORM_WIDTH)  # как и прежде создаем объкты класса Platform
                platforms.append(pf)
            if dieBlocks_layer.content2D[col][row]:
                bd = BlockDie(row * PLATFORM_WIDTH, col * PLATFORM_WIDTH)
                platforms.append(bd)

    teleports_layer = sprite_layers[4]
    for teleport in teleports_layer.objects:
        goX = int(teleport.properties["goX"]) * PLATFORM_WIDTH
        goY = int(teleport.properties["goY"]) * PLATFORM_HEIGHT
        x = teleport.x
        y = teleport.y - PLATFORM_HEIGHT
        tp = BlockTeleport(x, y, goX, goY)
        entities.add(tp)
        platforms.append(tp)
        animatedEntities.add(tp)

    playerX = 65
    playerY = 65

    monsters_layer = sprite_layers[3]
    for monster in monsters_layer.objects:
        try:
            x = monster.x
            y = monster.y
            if monster.name == "Player":
                playerX = x
                playerY = y - PLATFORM_HEIGHT
            elif monster.name == "Princess":
                pr = Princess(x, y - PLATFORM_HEIGHT)
                platforms.append(pr)
                entities.add(pr)
                animatedEntities.add(pr)
            else:
                up = int(monster.properties["up"])
                maxUp = int(monster.properties["maxUp"])
                left = int(monster.properties["left"])
                maxLeft = int(monster.properties["maxLeft"])
                mn = Monster(x, y - PLATFORM_HEIGHT, left, up, maxLeft, maxUp)
                entities.add(mn)
                platforms.append(mn)
                monsters.add(mn)
        except:
            print(u"Ошибка на слое монстров")

    total_level_width = platforms_layer.num_tiles_x * PLATFORM_WIDTH  # Высчитываем фактическую ширину уровня
    total_level_height = platforms_layer.num_tiles_y * PLATFORM_HEIGHT  # высоту

    return playerX, playerY, total_level_height, total_level_width, sprite_layers


def main():
    pygame.init()  # Инициация PyGame, обязательная строчка
    screen = pygame.display.set_mode(DISPLAY)  # Создаем окошко
    pygame.display.set_caption("Super Mario Boy")  # Пишем в шапку
    bg = Surface((WIN_WIDTH, WIN_HEIGHT))  # Создание видимой поверхности
    # будем использовать как фон

    renderer = helperspygame.RendererPygame()  # визуализатор

    playerX, playerY, total_level_height, total_level_width, sprite_layers = loadLevel("levels/map_1")
    bg.fill(Color("#000000"))  # Заливаем поверхность сплошным цветом

    left = right = up = running = False
    hero = Player(playerX, playerY)  # создаем героя по (x,y) координатам
    entities.add(hero)

    timer = pygame.time.Clock()

    camera = Camera(camera_configure, total_level_width, total_level_height)

    while not hero.winner:  # Основной цикл программы
        timer.tick(60)
        for e in pygame.event.get():  # Обрабатываем события
            if e.type == QUIT:
                return
            elif e.type == KEYDOWN:
                if e.key == K_UP:
                    up = True
                if e.key == K_LEFT:
                    left = True
                if e.key == K_RIGHT:
                    right = True
                if e.key == K_LSHIFT:
                    running = True
            elif e.type == KEYUP:
                if e.key == K_UP:
                    up = False
                if e.key == K_LEFT:
                    left = False
                if e.key == K_RIGHT:
                    right = False
                if e.key == K_LSHIFT:
                    running = False

        for sprite_layer in sprite_layers:  # перебираем все слои
            if not sprite_layer.is_object_group:  # и если это не слой объектов
                renderer.render_layer(screen, sprite_layer)  # отображаем его

        for e in entities:
            screen.blit(e.image, camera.apply(e))
        animatedEntities.update()  # показываеaм анимацию
        monsters.update(platforms)  # передвигаем всех монстров
        camera.update(hero)  # центризируем камеру относительно персонаж
        center_offset = camera.reverse(CENTER_OF_SCREEN)  # получаем координаты внутри длинного уровня
        renderer.set_camera_position_and_size(
            center_offset[0], center_offset[1], WIN_WIDTH, WIN_HEIGHT, "center")
        hero.update(left, right, up, running, platforms)  # передвижение
        pygame.display.update()  # обновление и вывод всех изменений на экран
        screen.blit(bg, (0, 0))  # Каждую итерацию необходимо всё перерисовывать
    for sprite_layer in sprite_layers:
        if not sprite_layer.is_object_group:
            renderer.render_layer(screen, sprite_layer)
    # когда заканчиваем уровень
    for e in entities:
        screen.blit(e.image, camera.apply(e))  # еще раз все перерисовываем
    font = pygame.font.Font(None, 38)
    text = font.render(("Thank you MarioBoy! but our princess is in another level!"), 1,
                       (255, 255, 255))  # выводим надпись
    screen.blit(text, (10, 100))
    pygame.display.update()


level = []
entities = pygame.sprite.Group()  # Все объекты
animatedEntities = pygame.sprite.Group()  # все анимированные объекты, за исключением героя
monsters = pygame.sprite.Group()  # Все передвигающиеся объекты
platforms = []  # то, во что мы будем врезаться или опираться
if __name__ == "__main__":
    main()
