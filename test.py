import pygame, sys, random

FILAS = 10
COLUMNAS = 10
CELL_SIZE = 64
GRID_WIDTH = COLUMNAS * CELL_SIZE
GRID_HEIGHT = FILAS * CELL_SIZE
MARGIN = 40
WINDOW_WIDTH = GRID_WIDTH + MARGIN * 2
WINDOW_HEIGHT = GRID_HEIGHT + MARGIN * 2 + 30
VELOCIDAD = 3
FPS = 60
FRAMES_POR_PASO = FPS // VELOCIDAD

COLOR_FONDO = (30, 30, 40)
COLOR_CELDA = (50, 50, 60)
COLOR_CAMINO = (100, 200, 100)
COLOR_RECORRIDO = (60, 120, 60)
COLOR_META = (255, 215, 0)
COLOR_INICIO = (0, 150, 255)
COLOR_REJILLA = (70, 70, 80)

class Nodo:
    def __init__(self, fila, columna):
        self.fila = fila
        self.columna = columna
        self.posicion = (fila, columna)
        self.caminable = True
        self.padre = None
        self.g = 0
        self.h = 0
        self.f = 0

matriz = [[Nodo(f, c) for c in range(COLUMNAS)] for f in range(FILAS)]

def mapeo(matriz):
    listaAbierta = []
    listaCerrada = []

    comienzo = matriz[0][0]
    meta = matriz[9][9]

    comienzo.h = heuristica(comienzo)
    comienzo.f = comienzo.h + comienzo.g
    listaAbierta.append(comienzo)

    while listaAbierta:
        nodo_actual = listaAbierta[0]
        for nodo in listaAbierta:
            if nodo.f < nodo_actual.f:
                nodo_actual = nodo

        listaAbierta.remove(nodo_actual)
        listaCerrada.append(nodo_actual)

        if nodo_actual == meta:
            camino = []
            actual = nodo_actual
            while actual is not None:
                camino.append(actual.posicion)
                actual = actual.padre
            return camino[::-1]

        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for VariableBusqueda, VariableBusqueda2 in direcciones:
            nuevaPos = nodo_actual.fila + VariableBusqueda
            nuevaPos2 = nodo_actual.columna + VariableBusqueda2

            if 0 <= nuevaPos < FILAS and 0 <= nuevaPos2 < COLUMNAS:
                vecino = matriz[nuevaPos][nuevaPos2]

                if not vecino.caminable or vecino in listaCerrada:
                    continue

                posible_g = nodo_actual.g + 1

                if vecino not in listaAbierta:
                    vecino.padre = nodo_actual
                    vecino.g = posible_g
                    vecino.h = heuristica(vecino)
                    vecino.f = vecino.g + vecino.h
                    listaAbierta.append(vecino)

                elif posible_g < vecino.g:
                    vecino.padre = nodo_actual
                    vecino.g = posible_g
                    vecino.f = vecino.g + vecino.h

    return None

def heuristica(nodo_actual):
    return abs(nodo_actual.fila - 9) + abs(nodo_actual.columna - 9)

def generar_obstaculos(matriz):
    for i in range(FILAS):
        for j in range(COLUMNAS):
            if random.random() < 0.3:
                matriz[i][j].caminable = False

    matriz[0][0].caminable = True
    matriz[9][9].caminable = True
    matriz[1][2].caminable = True
    matriz[2][1].caminable = True

generar_obstaculos(matriz)
camino_final = mapeo(matriz)

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("A* Pathfinding - Zombie Survival")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)

ruta_conjunto = set(camino_final) if camino_final else set()

zombie_sheet = pygame.image.load("sprites/craftpix-net-556605-free-zombie-sprite-sheet-pack-pixel-art/Zombie Man/Idle.png")
zombie_frame = zombie_sheet.subsurface((0, 0, 96, 96))
zombie_sprite = pygame.transform.scale(zombie_frame, (CELL_SIZE, CELL_SIZE))

raider_walk = pygame.image.load("sprites/craftpix-net-679950-free-raider-sprite-sheets-pixel-art/Raider_1/Walk.png")
raider_frames = []
for i in range(8):
    frame = raider_walk.subsurface((i * 128, 0, 128, 128))
    raider_frames.append(pygame.transform.scale(frame, (CELL_SIZE, CELL_SIZE)))

raider_idle_sheet = pygame.image.load("sprites/craftpix-net-679950-free-raider-sprite-sheets-pixel-art/Raider_1/Idle.png")
raider_idle = raider_idle_sheet.subsurface((0, 0, 128, 128))
raider_idle = pygame.transform.scale(raider_idle, (CELL_SIZE, CELL_SIZE))

paso_actual = 0
frame_anim = 0
contador_anim = 0
en_movimiento = camino_final is not None and len(camino_final) > 1

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if en_movimiento and paso_actual < len(camino_final) - 1:
        contador_anim += 1
        if contador_anim >= FRAMES_POR_PASO:
            contador_anim = 0
            paso_actual += 1
            frame_anim = (frame_anim + 1) % 8

    screen.fill(COLOR_FONDO)

    for f in range(FILAS):
        for c in range(COLUMNAS):
            x = MARGIN + c * CELL_SIZE
            y = MARGIN + f * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            nodo = matriz[f][c]

            if not nodo.caminable:
                screen.blit(zombie_sprite, rect)
            elif nodo == matriz[9][9]:
                pygame.draw.rect(screen, COLOR_META, rect)
                pygame.draw.rect(screen, COLOR_REJILLA, rect, 1)
            elif camino_final and (f, c) in ruta_conjunto:
            # Whether it's walked or not, show path color
                if paso_actual > 0 and (f, c) == camino_final[paso_actual - 1]:
                    pygame.draw.rect(screen, COLOR_RECORRIDO, rect)
                else:
                    pygame.draw.rect(screen, COLOR_CAMINO, rect)
                pygame.draw.rect(screen, COLOR_REJILLA, rect, 1)
            else:
                pygame.draw.rect(screen, COLOR_CELDA, rect)
                pygame.draw.rect(screen, COLOR_REJILLA, rect, 1)

    if camino_final:
        pos = camino_final[paso_actual]
        sx = MARGIN + pos[1] * CELL_SIZE
        sy = MARGIN + pos[0] * CELL_SIZE
        screen.blit(raider_frames[frame_anim], (sx, sy))
    else:
        screen.blit(raider_idle, (MARGIN, MARGIN))

    titulo = font.render("A* Pathfinding  -  Superviviente camina a la meta", True, (200, 200, 200))
    screen.blit(titulo, (MARGIN, GRID_HEIGHT + MARGIN + 5))

    if camino_final:
        info = font.render(f"Paso {paso_actual + 1} de {len(camino_final)}", True, (150, 255, 150))
    else:
        info = font.render("No se encontró un camino posible", True, (255, 100, 100))
    screen.blit(info, (MARGIN, GRID_HEIGHT + MARGIN + 5 + 22))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
