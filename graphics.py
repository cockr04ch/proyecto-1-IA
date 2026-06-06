import pygame
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, CELL_SIZE, MARGIN, GRID_HEIGHT,
    FILAS, COLUMNAS, META_POS, FPS, SIDEBAR_WIDTH, SIDEBAR_X,
    COLOR_FONDO, COLOR_CELDA, COLOR_CAMINO, COLOR_RECORRIDO,
    COLOR_META, COLOR_REJILLA, COLOR_SIDEBAR_BG,
    COLOR_BOTON, COLOR_BOTON_HOVER, COLOR_BOTON_TEXTO,
    BOTON_ANCHO, BOTON_ALTO,
)


def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("A* Pathfinding - Zombie Survival")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)
    return screen, clock, font


def load_sprites():
    zombie_sheet = pygame.image.load(
        "sprites/craftpix-net-556605-free-zombie-sprite-sheet-pack-pixel-art/Zombie Man/Idle.png"
    )
    zombie_frame = zombie_sheet.subsurface((0, 0, 96, 96))
    zombie_sprite = pygame.transform.scale(zombie_frame, (CELL_SIZE, CELL_SIZE))

    raider_walk = pygame.image.load(
        "sprites/craftpix-net-679950-free-raider-sprite-sheets-pixel-art/Raider_1/Walk.png"
    )
    raider_frames = []
    for i in range(8):
        frame = raider_walk.subsurface((i * 128, 0, 128, 128))
        raider_frames.append(pygame.transform.scale(frame, (CELL_SIZE, CELL_SIZE)))

    raider_idle_sheet = pygame.image.load(
        "sprites/craftpix-net-679950-free-raider-sprite-sheets-pixel-art/Raider_1/Idle.png"
    )
    raider_idle = raider_idle_sheet.subsurface((0, 0, 128, 128))
    raider_idle = pygame.transform.scale(raider_idle, (CELL_SIZE, CELL_SIZE))

    return zombie_sprite, raider_frames, raider_idle


def draw_grid(screen, matriz, camino, paso_actual, zombie_sprite):
    ruta_conjunto = set(camino) if camino else set()

    for f in range(FILAS):
        for c in range(COLUMNAS):
            x = MARGIN + c * CELL_SIZE
            y = MARGIN + f * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            nodo = matriz[f][c]

            if not nodo.caminable:
                screen.blit(zombie_sprite, rect)
            elif nodo == matriz[META_POS[0]][META_POS[1]]:
                pygame.draw.rect(screen, COLOR_META, rect)
                pygame.draw.rect(screen, COLOR_REJILLA, rect, 1)
            elif camino and (f, c) in ruta_conjunto:
                if paso_actual > 0 and (f, c) == camino[paso_actual - 1]:
                    pygame.draw.rect(screen, COLOR_RECORRIDO, rect)
                else:
                    pygame.draw.rect(screen, COLOR_CAMINO, rect)
                pygame.draw.rect(screen, COLOR_REJILLA, rect, 1)
            else:
                pygame.draw.rect(screen, COLOR_CELDA, rect)
                pygame.draw.rect(screen, COLOR_REJILLA, rect, 1)


def draw_character(screen, camino, paso_actual, raider_frames, frame_anim, raider_idle):
    if camino:
        pos = camino[paso_actual]
        sx = MARGIN + pos[1] * CELL_SIZE
        sy = MARGIN + pos[0] * CELL_SIZE
        screen.blit(raider_frames[frame_anim], (sx, sy))
    else:
        screen.blit(raider_idle, (MARGIN, MARGIN))


def draw_sidebar(screen, font, mouse_pos, paso_actual, total_pasos):
    sidebar_rect = pygame.Rect(SIDEBAR_X, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(screen, COLOR_SIDEBAR_BG, sidebar_rect)

    titulo = font.render("CONTROLES", True, (200, 200, 200))
    titulo_rect = titulo.get_rect(center=(SIDEBAR_X + SIDEBAR_WIDTH // 2, MARGIN + 15))
    screen.blit(titulo, titulo_rect)

    btn1_rect = pygame.Rect(SIDEBAR_X + 15, MARGIN + 50, BOTON_ANCHO, BOTON_ALTO)
    btn1_color = COLOR_BOTON_HOVER if btn1_rect.collidepoint(mouse_pos) else COLOR_BOTON
    pygame.draw.rect(screen, btn1_color, btn1_rect, border_radius=6)
    lbl1 = font.render("REGENERAR MAPA", True, COLOR_BOTON_TEXTO)
    screen.blit(lbl1, lbl1.get_rect(center=btn1_rect.center))

    btn2_rect = pygame.Rect(SIDEBAR_X + 15, MARGIN + 50 + BOTON_ALTO + 12, BOTON_ANCHO, BOTON_ALTO)
    btn2_color = COLOR_BOTON_HOVER if btn2_rect.collidepoint(mouse_pos) else COLOR_BOTON
    pygame.draw.rect(screen, btn2_color, btn2_rect, border_radius=6)
    lbl2 = font.render("REINICIAR", True, COLOR_BOTON_TEXTO)
    screen.blit(lbl2, lbl2.get_rect(center=btn2_rect.center))

    paso_label = font.render(f"Paso: {paso_actual + 1} / {total_pasos}", True, (180, 180, 200))
    screen.blit(paso_label, (SIDEBAR_X + 15, btn2_rect.bottom + 30))

    return btn1_rect, btn2_rect


def draw_info(screen, font, camino, paso_actual):
    titulo = font.render(
        "A* Pathfinding  -  Superviviente camina a la meta", True, (200, 200, 200)
    )
    screen.blit(titulo, (MARGIN, GRID_HEIGHT + MARGIN + 5))

    if camino:
        info = font.render(
            f"Paso {paso_actual + 1} de {len(camino)}", True, (150, 255, 150)
        )
    else:
        info = font.render(
            "No se encontró un camino posible", True, (255, 100, 100)
        )
    screen.blit(info, (MARGIN, GRID_HEIGHT + MARGIN + 5 + 22))
