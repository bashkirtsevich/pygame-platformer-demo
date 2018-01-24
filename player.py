import os

from pygame import *

import blocks
import monsters
import pyganim

STEP_SPEED = 1
MOVE_SPEED = 4
MOVE_EXTRA_SPEED = 3  # ускорение
WIDTH = 22
HEIGHT = 32
COLOR = "#888888"
JUMP_POWER = 8
JUMP_EXTRA_POWER = 2  # дополнительная сила прыжка
GRAVITY = 0.35  # Сила, которая будет тянуть нас вниз
ANIMATION_DELAY = 0.1  # скорость смены кадров
ANIMATION_SUPER_SPEED_DELAY = 0.05  # скорость смены кадров при ускорении
ICON_DIR = os.path.dirname(__file__)  # Полный путь к каталогу с файлами

ANIMATION_RIGHT = [('%s/mario/r1.png' % ICON_DIR),
                   ('%s/mario/r2.png' % ICON_DIR),
                   ('%s/mario/r3.png' % ICON_DIR),
                   ('%s/mario/r4.png' % ICON_DIR),
                   ('%s/mario/r5.png' % ICON_DIR)]
ANIMATION_LEFT = [('%s/mario/l1.png' % ICON_DIR),
                  ('%s/mario/l2.png' % ICON_DIR),
                  ('%s/mario/l3.png' % ICON_DIR),
                  ('%s/mario/l4.png' % ICON_DIR),
                  ('%s/mario/l5.png' % ICON_DIR)]
ANIMATION_JUMP_LEFT = [('%s/mario/jl.png' % ICON_DIR, 0.1)]
ANIMATION_JUMP_RIGHT = [('%s/mario/jr.png' % ICON_DIR, 0.1)]
ANIMATION_JUMP = [('%s/mario/j.png' % ICON_DIR, 0.1)]
ANIMATION_STAY = [('%s/mario/0.png' % ICON_DIR, 0.1)]


class Player(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.xvel = 0  # скорость перемещения. 0 - стоять на месте
        self.startX = x  # Начальная позиция Х, пригодится когда будем переигрывать уровень
        self.startY = y
        self.yvel = 0  # скорость вертикального перемещения
        self.onGround = False  # На земле ли я?
        self.isFly = False
        self.image = Surface((WIDTH, HEIGHT))
        self.image.fill(Color(COLOR))
        self.rect = Rect(x, y, WIDTH, HEIGHT)  # прямоугольный объект
        self.image.set_colorkey(Color(COLOR))  # делаем фон прозрачным
        #        Анимация движения вправо
        boltAnim = []
        boltAnimSuperSpeed = []
        for anim in ANIMATION_RIGHT:
            boltAnim.append((anim, ANIMATION_DELAY))
            boltAnimSuperSpeed.append((anim, ANIMATION_SUPER_SPEED_DELAY))
        self.boltAnimRight = pyganim.PygAnimation(boltAnim)
        self.boltAnimRight.play()
        self.boltAnimRightSuperSpeed = pyganim.PygAnimation(boltAnimSuperSpeed)
        self.boltAnimRightSuperSpeed.play()
        #        Анимация движения влево
        boltAnim = []
        boltAnimSuperSpeed = []
        for anim in ANIMATION_LEFT:
            boltAnim.append((anim, ANIMATION_DELAY))
            boltAnimSuperSpeed.append((anim, ANIMATION_SUPER_SPEED_DELAY))
        self.boltAnimLeft = pyganim.PygAnimation(boltAnim)
        self.boltAnimLeft.play()
        self.boltAnimLeftSuperSpeed = pyganim.PygAnimation(boltAnimSuperSpeed)
        self.boltAnimLeftSuperSpeed.play()

        self.boltAnimStay = pyganim.PygAnimation(ANIMATION_STAY)
        self.boltAnimStay.play()
        self.boltAnimStay.blit(self.image, (0, 0))  # По-умолчанию, стоим

        self.boltAnimJumpLeft = pyganim.PygAnimation(ANIMATION_JUMP_LEFT)
        self.boltAnimJumpLeft.play()

        self.boltAnimJumpRight = pyganim.PygAnimation(ANIMATION_JUMP_RIGHT)
        self.boltAnimJumpRight.play()

        self.boltAnimJump = pyganim.PygAnimation(ANIMATION_JUMP)
        self.boltAnimJump.play()
        self.winner = False

    def update(self, left, right, up, running, platforms):

        if up:
            if self.onGround:  # прыгаем, только когда можем оттолкнуться от земли
                self.yvel = -JUMP_POWER
                if running and (left or right):  # если есть ускорение и мы движемся
                    self.yvel -= JUMP_EXTRA_POWER  # то прыгаем выше

        if left:
            if self.xvel < 0:
                self.xvel = -MOVE_SPEED  # Лево = x- n
            else:
                self.xvel = -STEP_SPEED
            if running:  # если усkорение
                self.xvel -= MOVE_EXTRA_SPEED  # то передвигаемся быстрее

        if right:
            if self.xvel > 0:
                self.xvel = MOVE_SPEED
            else:
                self.xvel = STEP_SPEED
            if running:  # если усkорение
                self.xvel += MOVE_EXTRA_SPEED  # то передвигаемся быстрее

        self.image.fill(Color(COLOR))
        if self.isFly:
            if self.xvel < 0:
                self.boltAnimJumpLeft.blit(self.image, (0, 0))  # отображаем анимацию прыжка
            elif self.xvel > 0:
                self.boltAnimJumpRight.blit(self.image, (0, 0))
            else:
                self.boltAnimJump.blit(self.image, (0, 0))
        else:
            if running:
                if self.xvel < 0:
                    self.boltAnimLeftSuperSpeed.blit(self.image, (0, 0))  # отображаем анимацию движения
                elif self.xvel > 0:
                    self.boltAnimRightSuperSpeed.blit(self.image, (0, 0))
                else:
                    self.boltAnimStay.blit(self.image, (0, 0))
            else:
                if self.xvel < 0:
                    self.boltAnimLeft.blit(self.image, (0, 0))  # отображаем анимацию движения
                elif self.xvel > 0:
                    self.boltAnimRight.blit(self.image, (0, 0))
                else:
                    self.boltAnimStay.blit(self.image, (0, 0))

        if not (left or right) and not self.isFly:  # стоим, когда нет указаний идти
            self.xvel = 0

        if not self.onGround:
            self.yvel += GRAVITY

        if abs(round(self.yvel)) > 2:
            self.isFly = True
        elif self.onGround:
            self.isFly = False

        self.onGround = False
        self.rect.y += self.yvel
        self.collide(0, self.yvel, platforms)

        self.rect.x += self.xvel  # переносим свои положение на xvel
        self.collide(self.xvel, 0, platforms)

    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if sprite.collide_rect(self, p):  # если есть пересечение платформы с игроком
                if isinstance(p, blocks.BlockDie) or isinstance(p,
                                                                monsters.Monster):  # если пересакаемый блок - blocks.BlockDie или Monster
                    self.die()  # умираем
                if isinstance(p, blocks.BlockTeleport):
                    self.teleporting(p.goX, p.goY)
                elif isinstance(p, blocks.Princess):  # если коснулись принцессы
                    self.winner = True  # победили!!!
                else:
                    if xvel > 0:  # если движется вправо
                        self.rect.right = p.rect.left  # то не движется вправо
                        self.xvel = 0

                    if xvel < 0:  # если движется влево
                        self.rect.left = p.rect.right  # то не движется влево
                        self.xvel = 0

                    if yvel > 0:  # если падает вниз
                        self.rect.bottom = p.rect.top  # то не падает вниз
                        self.onGround = True  # и становится на что-то твердое
                        self.yvel = 0  # и энергия падения пропадает

                    if yvel < 0:  # если движется вверх
                        self.rect.top = p.rect.bottom  # то не движется вверх
                        self.yvel = 0  # и энергия прыжка пропадает

    def teleporting(self, goX, goY):
        self.rect.x = goX
        self.rect.y = goY

    def die(self):
        time.wait(1000)
        self.xvel = 0
        self.yvel = 0
        self.teleporting(self.startX, self.startY)  # перемещаемся в начальные координаты
