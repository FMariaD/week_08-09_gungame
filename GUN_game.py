import pygame as pg
import numpy as np
from random import randint

SCREEN_SIZE = (800, 700)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
MAROON = (128, 0, 0)
OLIVE = (0, 128, 128)
FPS = 30

pg.init()

screen = pg.display.set_mode(SCREEN_SIZE)
SCREEN_SIZE = (SCREEN_SIZE[0], SCREEN_SIZE[1] - 100)
pg.display.set_caption("The gun of Khiryanov")
clock = pg.time.Clock()
screen.fill(BLACK)
font = pg.font.Font(None, 50)
g = 10  # ускорение свободного падения
k = 0.9  # коэффициент замедления при ударении со стенками
counter = 0  # переменная для времени
score = 0  # счет


class Ball:
    def __init__(self, coord, vel, t0):
        self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.coord = coord
        self.vel = vel
        self.rad = 15
        self.is_alive = True
        self.time = t0  # когда заспавнили шарик

    def draw(self):
        pg.draw.circle(screen, self.color, self.coord, self.rad)

    def check_walls(self, v):
        if self.coord[0] < self.rad:
            self.coord[0] = self.rad
            self.vel[0] = (-k) * v[0]
        elif self.coord[0] > SCREEN_SIZE[0] - self.rad:
            self.coord[0] = SCREEN_SIZE[0] - self.rad
            self.vel[0] = (-k) * v[0]

    def move(self, t):
        self.vel = list(self.vel)
        self.coord = list(self.coord)
        vel_y = self.vel[1] + g * (t - self.time) / FPS
        self.coord[0] = self.coord[0] + int(self.vel[0])
        self.coord[1] = self.coord[1] + int(vel_y)
        self.check_walls((self.vel[0], vel_y))
        if self.coord[1] > (SCREEN_SIZE[1] + 2*self.rad):
            self.is_alive = False


class Cannon:
    def __init__(self):
        self.coord = (0, 300)
        self.angle = 0
        self.min_pow = 20
        self.max_pow = 50
        self.power = randint(self.min_pow, self.max_pow)
        self.active = False

    def draw(self):
        end_pos = (int(self.coord[0] + self.power * 2 * np.cos(self.angle)),
                   int(self.coord[1] + self.power * 2 * np.sin(self.angle)))
        pg.draw.line(screen, WHITE, self.coord, end_pos, 5)
        return end_pos

    def strike(self):
        vel = (int(self.power * np.cos(self.angle)),
               int(self.power * np.sin(self.angle)))
        self.active = False
        return vel

    def set_angle(self, mouse_pos):
        self.angle = np.arctan2(mouse_pos[1] - self.coord[1],
                                mouse_pos[0] - self.coord[0])


class Target:
    def __init__(self):
        self.coords = (randint(50, 750), randint(50, 550))
        self.radius = 30
        self.is_alive = True

    def draw(self):
        pg.draw.circle(screen, RED, self.coords, self.radius)
        pg.draw.circle(screen, WHITE, self.coords, self.radius - 10)
        pg.draw.circle(screen, RED, self.coords, self.radius - 20)

    def hit_check(self, xy, ball_radius):
        (ball_x, ball_y) = xy
        (x, y) = self.coords
        distance = ((ball_x - x) ** 2 + (ball_y - y) ** 2) ** 0.5
        if distance <= (self.radius + ball_radius):
            self.is_alive = False
            return 1
        else:
            return 0


def clock_and_score_renewal(time0, score0):
    time_passed = int(time0 / FPS)
    if time_passed < 60:
        str_format_time = "Time:  " + str(time_passed) + "s"
    else:
        str_format_time = "Time:  " + str(time_passed // 60) + "m  " + \
                          str(time_passed % 60) + "s"
    text2 = font.render(str_format_time, True, OLIVE)
    str_format_score = "Score:  " + str(score0)
    text3 = font.render(str_format_score, True, MAROON)
    pg.draw.rect(screen, WHITE, (0, 600, 800, 100))
    screen.blit(text2, (500, 650))
    screen.blit(text3, (150, 650))


target = Target()
gun = Cannon()
pg.display.update()
finished = False
ball_list = []
ball_new_list = []

while not finished:
    clock.tick(FPS)
    counter += 1
    screen.fill(BLACK)
    if not target.is_alive:
        target = Target()
    target.draw()
    gun_end = gun.draw()
    ball_new_list = []
    for ball in ball_list:
        ball.move(counter)
        score += target.hit_check(ball.coord, ball.rad)
        if ball.is_alive:
            ball.draw()
            ball_new_list.append(ball)  # отсеивает мёртвые шары
    ball_list = ball_new_list
    for event in pg.event.get():
        if event.type == pg.QUIT:
            finished = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            gun.set_angle(event.pos)
            ball_list.append(Ball(gun_end, gun.strike(), counter))
    clock_and_score_renewal(counter, score)
    pg.display.update()

pg.quit()