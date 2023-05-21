import pygame
import numpy as np

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
GRAVITY = 0.5
JUMP_HEIGHT = 100
JUMP_DURATION = 500
JUMP_VELOCITY = -10


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hermite Interpolation vs. Linear Motion")

player_image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
player_image.fill((255, 0, 0))

player1_x = 100
player1_y = SCREEN_HEIGHT - PLAYER_HEIGHT
player1_vy = 0
player1_on_ground = True
player2_x = SCREEN_WIDTH - 100 - PLAYER_WIDTH
player2_y = SCREEN_HEIGHT - PLAYER_HEIGHT
player2_vy = 0
player2_on_ground = True


def hermite_interpolation(t, p0, p1, v0, v1):
    t2 = t * t
    t3 = t2 * t
    h00 = 2 * t3 - 3 * t2 + 1
    h01 = -2 * t3 + 3 * t2
    h10 = t3 - 2 * t2 + t
    h11 = t3 - t2
    return h00 * p0 + h01 * p1 + h10 * v0 + h11 * v1


clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if player1_on_ground:
        player1_vy = 0
    else:
        player1_y += player1_vy
        player1_vy += GRAVITY
        if player1_y + PLAYER_HEIGHT > SCREEN_HEIGHT:
            player1_y = SCREEN_HEIGHT - PLAYER_HEIGHT
            player1_vy = 0
            player1_on_ground = True
    if pygame.key.get_pressed()[pygame.K_q] and player1_on_ground:
        jump_start_y = player1_y
        jump_start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - jump_start_time < JUMP_DURATION:
            t = (pygame.time.get_ticks() - jump_start_time) / JUMP_DURATION
            player1_y = hermite_interpolation(
                t, jump_start_y, jump_start_y - JUMP_HEIGHT, 0, 0)
            screen.fill((255, 255, 255))
            screen.blit(player_image, (player1_x, player1_y))
            screen.blit(player_image, (player2_x, player2_y))
            pygame.display.update()
            clock.tick(60)
        player1_vy = -JUMP_HEIGHT / (JUMP_DURATION / 2)
        player1_on_ground = False

    if player2_on_ground:
        player2_vy = 0
    else:
        player2_y += player2_vy
        player2_vy += GRAVITY
        if player2_y + PLAYER_HEIGHT > SCREEN_HEIGHT:
            player2_y = SCREEN_HEIGHT - PLAYER_HEIGHT
            player2_vy = 0
            player2_on_ground = True
    if pygame.key.get_pressed()[pygame.K_e] and player2_on_ground:
        player2_vy = JUMP_VELOCITY
        player2_on_ground = False

    screen.fill((255, 255, 255))
    screen.blit(player_image, (player1_x, player1_y))
    screen.blit(player_image, (player2_x, player2_y))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
