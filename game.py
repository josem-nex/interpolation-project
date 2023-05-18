import pygame
import random
import numpy as np

# Dimensiones de la ventana
WIDTH = 640
HEIGHT = 480

# Tamaño de la celda
CELL_SIZE = 20

# Definición de colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Inicialización de Pygame
pygame.init()

# Creación de la ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")

# Fuente para el texto
font = pygame.font.SysFont('Arial', 24)

# Función para dibujar una celda


def draw_cell(cell, color):
    pygame.draw.rect(screen, color, (cell[0], cell[1], CELL_SIZE, CELL_SIZE))

# Función para generar una posición aleatoria dentro de la cuadrícula


def generate_random_position():
    x = random.randrange(0, WIDTH, CELL_SIZE)
    y = random.randrange(0, HEIGHT, CELL_SIZE)
    return [x, y]

# Función para generar la trayectoria de la serpiente hacia la comida


def generate_snake_path(snake_head, food):
    # Generar una interpolación lineal entre la cabeza de la serpiente y la comida
    if food[0] != snake_head[0]:
        m = (food[1] - snake_head[1]) / (food[0] - snake_head[0])
        b = snake_head[1] - m * snake_head[0]
        def interp_func(x): return int(m * x + b)

        # Generar la trayectoria de la serpiente a partir de la interpolación lineal
        snake_path = []
        if snake_head[0] < food[0]:
            for i in range(snake_head[0], food[0], CELL_SIZE):
                x_pos = i + CELL_SIZE//2
                y_pos = interp_func(x_pos)
                snake_path.append([x_pos, y_pos])
        else:
            for i in range(snake_head[0], food[0], -CELL_SIZE):
                x_pos = i - CELL_SIZE//2
                y_pos = interp_func(x_pos)
                snake_path.append([x_pos, y_pos])
    else:
        # Si la comida está en la misma columna que la cabeza de la serpiente, moverse verticalmente
        snake_path = []
        if snake_head[1] < food[1]:
            for i in range(snake_head[1], food[1], CELL_SIZE):
                x_pos = snake_head[0] + CELL_SIZE//2
                y_pos = i + CELL_SIZE//2
                snake_path.append([x_pos, y_pos])
        else:
            for i in range(snake_head[1], food[1], -CELL_SIZE):
                x_pos = snake_head[0] + CELL_SIZE//2
                y_pos = i - CELL_SIZE//2
                snake_path.append([x_pos, y_pos])

    return snake_path


# Generación de la serpiente
snake = [[WIDTH//2, HEIGHT//2]]
snake_path = [snake[0]]

# Generación de la comida
food = generate_random_position()

# Dirección de la serpiente
dx = CELL_SIZE
dy = 0

# Variables para el control del juego
clock = pygame.time.Clock()
game_over_flag = False
score = 0

# Bucle principal del juego
while not game_over_flag:
    # Manejo de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over_flag = True

    # Movimiento de la serpiente
    snake_head = [snake[-1][0] + dx, snake[-1][1] + dy]
    if snake_head == food:
        # Si la serpiente come la comida, agregar una celda a la cola
        snake.append(snake_head)
        score += 1
        food = generate_random_position()
    else:
        # Si la serpiente no come la comida, mover la cola y la cabeza
        snake = snake[1:] + [snake_head]

    # Generar la trayectoria de la serpiente hacia la comida
    snake_path = generate_snake_path(snake_head, food)

    # Verificar si la serpiente choca con una pared o consigo misma
    if snake_head[0] < 0 or snake_head[0] >= WIDTH or snake_head[1] < 0 or snake_head[1] >= HEIGHT or snake_head in snake[:-1]:
        game_over_flag = True

    # Dibujado de la pantalla
    screen.fill(WHITE)
    draw_cell(food, RED)
    for cell in snake:
        draw_cell(cell, GREEN)
    score_text = font.render('Score: {}'.format(score), True, BLACK)
    screen.blit(score_text, (10, 10))
    pygame.display.update()

    # Actualización del reloj
    clock.tick(5)

    # Mover la serpiente hacia la comida mediante interpolación polinómica
    if len(snake_path) > 1:
        m = (snake_path[1][1] - snake_path[0][1]) / \
            (snake_path[1][0] - snake_path[0][0])
        b = snake_path[0][1] - m * snake_path[0][0]
        interp_func = np.poly1d([m, b])
        if snake_head[0] < food[0]:
            snake_head[0] = min(snake_head[0] + CELL_SIZE, food[0])
        elif snake_head[0] > food[0]:
            snake_head[0] = max(snake_head[0] - CELL_SIZE, food[0])
        y_val = interp_func(snake_head[0])
        if np.isnan(y_val):
            if snake_head[1] < food[1]:
                snake_head[1] = min(snake_head[1] + CELL_SIZE, food[1])
            elif snake_head[1] > food[1]:
                snake_head[1] = max(snake_head[1] - CELL_SIZE, food[1])
        else:
            snake_head[1] = int(y_val)
        dx = np.sign(food[0] - snake_head[0]) * CELL_SIZE
        dy = int(interp_func(snake_head[0] + dx) - snake_head[1])
