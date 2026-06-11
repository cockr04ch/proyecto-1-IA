import pygame
from config import (
    MARGIN, SIDEBAR_WIDTH, COMP_GAP,
    COLOR_FONDO, COLOR_CELDA, COLOR_CAMINO_ASTAR, COLOR_CAMINO_BFS,
    COLOR_EXPLORADOS_ASTAR, COLOR_EXPLORADOS_BFS,
    COLOR_META, COLOR_INICIO, COLOR_REJILLA, COLOR_PANEL,
    COLOR_SIDEBAR_BG, COLOR_BOTON, COLOR_BOTON_HOVER,
    COLOR_BOTON_ACTIVO, COLOR_BOTON_TEXTO, BOTON_ANCHO, BOTON_ALTO,
)


def init_pygame(ancho, alto):
    pygame.init()
    screen = pygame.display.set_mode((ancho, alto))
    pygame.display.set_caption("A* vs BFS Pathfinding - Zombie Survival")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)
    font_bold = pygame.font.SysFont("Arial", 16, bold=True)
    font_small = pygame.font.SysFont("Arial", 14)
    return screen, clock, font, font_bold, font_small


def load_sprites(cell_size):
    zombie_sheet = pygame.image.load(
        "sprites/craftpix-net-556605-free-zombie-sprite-sheet-pack-pixel-art/Zombie Man/Idle.png"
    )
    zombie_frame = zombie_sheet.subsurface((0, 0, 96, 96))
    zombie_sprite = pygame.transform.scale(zombie_frame, (cell_size, cell_size))

    raider_walk = pygame.image.load(
        "sprites/craftpix-net-679950-free-raider-sprite-sheets-pixel-art/Raider_1/Walk.png"
    )
    raider_frames = []
    for i in range(8):
        frame = raider_walk.subsurface((i * 128, 0, 128, 128))
        raider_frames.append(pygame.transform.scale(frame, (cell_size, cell_size)))

    raider_idle_sheet = pygame.image.load(
        "sprites/craftpix-net-679950-free-raider-sprite-sheets-pixel-art/Raider_1/Idle.png"
    )
    raider_idle = raider_idle_sheet.subsurface((0, 0, 128, 128))
    raider_idle = pygame.transform.scale(raider_idle, (cell_size, cell_size))

    return zombie_sprite, raider_frames, raider_idle


def _color_calor(dist, max_dist):
    t = 1.0 - (dist / max_dist) if max_dist > 0 else 1.0
    base = (50, 50, 60)
    calido = (75, 55, 40)
    r = int(base[0] + (calido[0] - base[0]) * t)
    g = int(base[1] + (calido[1] - base[1]) * t)
    b = int(base[2] + (calido[2] - base[2]) * t)
    return (r, g, b)


def crear_superficie_calor(filas, columnas, cell_size):
    grid_w = columnas * cell_size
    grid_h = filas * cell_size
    superficie = pygame.Surface((grid_w, grid_h))
    meta = (filas - 1, columnas - 1)
    max_dist = meta[0] + meta[1]
    for f in range(filas):
        for c in range(columnas):
            dist = abs(f - meta[0]) + abs(c - meta[1])
            color = _color_calor(dist, max_dist)
            superficie.fill(color, (c * cell_size, f * cell_size, cell_size, cell_size))
    return superficie


def _dibujar_heuristicas(screen, font_small, matriz, cell_size, ox, oy):
    filas = len(matriz)
    columnas = len(matriz[0])
    meta = (filas - 1, columnas - 1)
    for f in range(filas):
        for c in range(columnas):
            if not matriz[f][c].caminable:
                continue
            h = abs(f - meta[0]) + abs(c - meta[1])
            x = ox + c * cell_size
            y = oy + f * cell_size
            text = font_small.render(str(h), True, (130, 130, 140))
            tx = x + (cell_size - text.get_width()) // 2
            ty = y + (cell_size - text.get_height()) // 2
            screen.blit(text, (tx, ty))


def _draw_tooltip(screen, font_small, mouse_pos, matriz, cell_size, ox, oy,
                  explorados_list, camino, titulo, color_algo):
    mx, my = mouse_pos
    filas = len(matriz)
    columnas = len(matriz[0])
    grid_w = columnas * cell_size
    grid_h = filas * cell_size
    if mx < ox or mx >= ox + grid_w or my < oy or my >= oy + grid_h:
        return
    c = (mx - ox) // cell_size
    f = (my - oy) // cell_size
    if f >= filas or c >= columnas:
        return
    pos = (f, c)
    nodo = matriz[f][c]
    if not nodo.caminable:
        return
    meta = (filas - 1, columnas - 1)
    h = abs(f - meta[0]) + abs(c - meta[1])
    expl_set = set(explorados_list) if explorados_list else set()
    path_set = set(camino) if camino else set()
    partes = [f"h={h}"]
    if pos in expl_set:
        partes.append("explorado")
    if pos in path_set:
        partes.append("camino")
    text = " | ".join(partes)
    surf = font_small.render(f"{titulo}: {text}", True, (220, 220, 220))
    pad = 5
    tw, th = surf.get_size()
    tx = min(mx + 12, screen.get_width() - tw - pad * 2 - 10)
    ty = my - th - 10
    if ty < 0:
        ty = my + 12
    bg = pygame.Rect(tx, ty, tw + pad * 2, th + pad * 2)
    pygame.draw.rect(screen, (20, 20, 30), bg, border_radius=4)
    pygame.draw.rect(screen, color_algo, bg, 1, border_radius=4)
    screen.blit(surf, (tx + pad, ty + pad))


def _draw_grid_at(screen, matriz, cell_size, ox, oy,
                  camino, explorados_list, revelados, paso_actual,
                  color_camino, color_explorados,
                  zombie_sprite, raider_frames, frame_anim, raider_idle,
                  heat_surf=None, font_small=None, mostrar_h=False):
    filas = len(matriz)
    columnas = len(matriz[0])
    ruta_set = set(camino) if camino else set()
    explorados_set = set(explorados_list[:revelados]) if explorados_list else set()
    meta_pos = (filas - 1, columnas - 1)
    grid_w = columnas * cell_size
    grid_h = filas * cell_size

    if heat_surf:
        screen.blit(heat_surf, (ox, oy))
    else:
        pygame.draw.rect(screen, COLOR_CELDA, (ox, oy, grid_w, grid_h))

    if mostrar_h and font_small:
        _dibujar_heuristicas(screen, font_small, matriz, cell_size, ox, oy)

    overlay = pygame.Surface((grid_w, grid_h), pygame.SRCALPHA)
    for pos in ruta_set:
        pr = pygame.Rect(pos[1] * cell_size, pos[0] * cell_size, cell_size, cell_size)
        pygame.draw.rect(overlay, (*color_camino, 160), pr)
    for pos in explorados_set:
        if pos not in ruta_set:
            er = pygame.Rect(pos[1] * cell_size, pos[0] * cell_size, cell_size, cell_size)
            pygame.draw.rect(overlay, (*color_explorados, 80), er)
    screen.blit(overlay, (ox, oy))

    for f in range(filas):
        for c in range(columnas):
            x = ox + c * cell_size
            y = oy + f * cell_size
            pos = (f, c)
            nodo = matriz[f][c]

            if pos == meta_pos:
                pygame.draw.rect(screen, COLOR_META, (x, y, cell_size, cell_size))
            elif pos == (0, 0):
                pygame.draw.rect(screen, COLOR_INICIO, (x, y, cell_size, cell_size))

            pygame.draw.rect(screen, COLOR_REJILLA, (x, y, cell_size, cell_size), 1)

            if not nodo.caminable:
                screen.blit(zombie_sprite, (x, y))

    if camino and paso_actual < len(camino):
        pos = camino[paso_actual]
        sx = ox + pos[1] * cell_size
        sy = oy + pos[0] * cell_size
        screen.blit(raider_frames[frame_anim], (sx, sy))
    elif not camino:
        screen.blit(raider_idle, (ox, oy))


def draw_grid_normal(screen, matriz, cell_size,
                     camino, explorados_list, revelados, paso_actual,
                     zombie_sprite, raider_frames, frame_anim, raider_idle,
                     heat_surf=None, font_small=None):
    _draw_grid_at(
        screen, matriz, cell_size, MARGIN, MARGIN,
        camino, explorados_list, revelados, paso_actual,
        COLOR_CAMINO_ASTAR, COLOR_EXPLORADOS_ASTAR,
        zombie_sprite, raider_frames, frame_anim, raider_idle,
        heat_surf, font_small, mostrar_h=True,
    )


def draw_comparison_view(screen, matriz, cell_size,
                         camino_a, expl_a, revelados_a, paso_a,
                         camino_b, expl_b, revelados_b, paso_b,
                         zombie_sprite, raider_frames, frame_anim_a,
                         frame_anim_b, raider_idle,
                         font, font_bold, tiempo_a, tiempo_b,
                         heat_surf=None, font_small=None, mouse_pos=None):
    filas = len(matriz)
    columnas = len(matriz[0])
    grid_w = columnas * cell_size
    grid_h = filas * cell_size

    ox = MARGIN
    oy = MARGIN + 20

    tit_a = font_bold.render("A* Pathfinding", True, COLOR_CAMINO_ASTAR)
    screen.blit(tit_a, (ox + 4, MARGIN))

    _draw_grid_at(
        screen, matriz, cell_size, ox, oy,
        camino_a, expl_a, revelados_a, paso_a,
        COLOR_CAMINO_ASTAR, COLOR_EXPLORADOS_ASTAR,
        zombie_sprite, raider_frames, frame_anim_a, raider_idle,
        heat_surf,
    )

    if revelados_a < len(expl_a):
        lbl_a = font.render(f"Explorando: {revelados_a}/{len(expl_a)}", True, COLOR_EXPLORADOS_ASTAR)
    elif camino_a:
        lbl_a = font.render(f"Paso {paso_a + 1}/{len(camino_a)}", True, COLOR_CAMINO_ASTAR)
    else:
        lbl_a = font.render("Sin camino", True, (255, 100, 100))
    screen.blit(lbl_a, (ox, oy + grid_h + 4))

    ox2 = ox + grid_w + COMP_GAP

    tit_b = font_bold.render("BFS (Anchura)", True, COLOR_CAMINO_BFS)
    screen.blit(tit_b, (ox2 + 4, MARGIN))

    _draw_grid_at(
        screen, matriz, cell_size, ox2, oy,
        camino_b, expl_b, revelados_b, paso_b,
        COLOR_CAMINO_BFS, COLOR_EXPLORADOS_BFS,
        zombie_sprite, raider_frames, frame_anim_b, raider_idle,
        heat_surf,
    )

    if revelados_b < len(expl_b):
        lbl_b = font.render(f"Explorando: {revelados_b}/{len(expl_b)}", True, COLOR_EXPLORADOS_BFS)
    elif camino_b:
        lbl_b = font.render(f"Paso {paso_b + 1}/{len(camino_b)}", True, COLOR_CAMINO_BFS)
    else:
        lbl_b = font.render("Sin camino", True, (255, 100, 100))
    screen.blit(lbl_b, (ox2, oy + grid_h + 4))

    _draw_metrics(screen, font, font_bold,
                  camino_a, expl_a, tiempo_a,
                  camino_b, expl_b, tiempo_b,
                  oy + grid_h + 28, columnas, cell_size)

    if font_small and mouse_pos:
        _draw_tooltip(screen, font_small, mouse_pos, matriz, cell_size, ox, oy,
                      expl_a, camino_a, "A*", COLOR_CAMINO_ASTAR)
        _draw_tooltip(screen, font_small, mouse_pos, matriz, cell_size, ox2, oy,
                      expl_b, camino_b, "BFS", COLOR_CAMINO_BFS)


def _draw_metrics(screen, font, font_bold,
                  camino_a, expl_a, tiempo_a,
                  camino_b, expl_b, tiempo_b, y, columnas, cell_size):
    grid_w = columnas * cell_size
    panel_w = grid_w * 2 + COMP_GAP
    panel_h = 115
    panel_rect = pygame.Rect(MARGIN, y, panel_w, panel_h)
    pygame.draw.rect(screen, COLOR_PANEL, panel_rect, border_radius=8)
    pygame.draw.rect(screen, (50, 50, 60), panel_rect, 2, border_radius=8)

    title = font_bold.render("COMPARACIÓN DE ALGORITMOS", True, (220, 220, 220))
    tx = MARGIN + (panel_w - title.get_width()) // 2
    screen.blit(title, (tx, y + 8))

    mid_x = MARGIN + grid_w + COMP_GAP // 2

    pygame.draw.line(screen, (50, 50, 60), (mid_x, y + 30), (mid_x, y + panel_h - 8), 2)

    screen.blit(font_bold.render("A*", True, COLOR_CAMINO_ASTAR), (MARGIN + 12, y + 32))
    screen.blit(font_bold.render("BFS", True, COLOR_CAMINO_BFS), (mid_x + 12, y + 32))

    a_len = len(camino_a) if camino_a else 0
    b_len = len(camino_b) if camino_b else 0

    screen.blit(font.render(f"Camino: {a_len} pasos", True, (200, 200, 200)), (MARGIN + 12, y + 52))
    screen.blit(font.render(f"Camino: {b_len} pasos", True, (200, 200, 200)), (mid_x + 12, y + 52))

    screen.blit(font.render(f"Explorados: {len(expl_a)}", True, (180, 180, 180)), (MARGIN + 12, y + 72))
    screen.blit(font.render(f"Explorados: {len(expl_b)}", True, (180, 180, 180)), (mid_x + 12, y + 72))

    screen.blit(font.render(f"Tiempo: {tiempo_a * 1000:.2f}ms", True, (180, 180, 180)), (MARGIN + 12, y + 92))
    screen.blit(font.render(f"Tiempo: {tiempo_b * 1000:.2f}ms", True, (180, 180, 180)), (mid_x + 12, y + 92))


def draw_sidebar(screen, font, mouse_pos,
                 paso_astar, total_astar,
                 paso_bfs, total_bfs,
                 tiempo_astar, tiempo_bfs,
                 modo_comparacion, sidebar_x, window_height,
                 revelados_astar, total_expl_astar,
                 revelados_bfs=None, total_expl_bfs=None):
    sx = sidebar_x

    pygame.draw.rect(screen, COLOR_SIDEBAR_BG, (sx, 0, SIDEBAR_WIDTH, window_height))

    titulo = font.render("CONTROLES", True, (200, 200, 200))
    titulo_rect = titulo.get_rect(center=(sx + SIDEBAR_WIDTH // 2, MARGIN + 15))
    screen.blit(titulo, titulo_rect)

    btn1_rect = pygame.Rect(sx + 15, MARGIN + 50, BOTON_ANCHO, BOTON_ALTO)
    btn1_color = COLOR_BOTON_HOVER if btn1_rect.collidepoint(mouse_pos) else COLOR_BOTON
    pygame.draw.rect(screen, btn1_color, btn1_rect, border_radius=6)
    lbl1 = font.render("REGENERAR MAPA", True, COLOR_BOTON_TEXTO)
    screen.blit(lbl1, lbl1.get_rect(center=btn1_rect.center))

    btn2_rect = pygame.Rect(sx + 15, MARGIN + 50 + BOTON_ALTO + 10, BOTON_ANCHO, BOTON_ALTO)
    btn2_color = COLOR_BOTON_HOVER if btn2_rect.collidepoint(mouse_pos) else COLOR_BOTON
    pygame.draw.rect(screen, btn2_color, btn2_rect, border_radius=6)
    lbl2 = font.render("REINICIAR", True, COLOR_BOTON_TEXTO)
    screen.blit(lbl2, lbl2.get_rect(center=btn2_rect.center))

    btn3_rect = pygame.Rect(sx + 15, MARGIN + 50 + (BOTON_ALTO + 10) * 2, BOTON_ANCHO, BOTON_ALTO)
    btn3_color = COLOR_BOTON_ACTIVO if modo_comparacion else (
        COLOR_BOTON_HOVER if btn3_rect.collidepoint(mouse_pos) else COLOR_BOTON
    )
    pygame.draw.rect(screen, btn3_color, btn3_rect, border_radius=6)
    lbl3_txt = "MODO NORMAL" if modo_comparacion else "COMPARAR A* vs BFS"
    lbl3 = font.render(lbl3_txt, True, COLOR_BOTON_TEXTO)
    screen.blit(lbl3, lbl3.get_rect(center=btn3_rect.center))

    y_info = btn3_rect.bottom + 20

    modo_label = font.render(
        "Modo: COMPARACIÓN" if modo_comparacion else "Modo: NORMAL",
        True,
        COLOR_CAMINO_BFS if modo_comparacion else COLOR_CAMINO_ASTAR,
    )
    screen.blit(modo_label, (sx + 15, y_info))

    if modo_comparacion:
        y_line = y_info + 22
        if total_expl_bfs is not None and revelados_bfs is not None and revelados_bfs < total_expl_bfs:
            a_line = f"A* exploración: {revelados_astar}/{total_expl_astar}"
            b_line = f"BFS exploración: {revelados_bfs}/{total_expl_bfs}"
        else:
            a_line = f"A*: {paso_astar + 1}/{total_astar if total_astar else 0}"
            b_line = f"BFS: {paso_bfs + 1}/{total_bfs if total_bfs else 0}"
        screen.blit(font.render(a_line, True, COLOR_CAMINO_ASTAR), (sx + 15, y_line))
        screen.blit(font.render(b_line, True, COLOR_CAMINO_BFS), (sx + 15, y_line + 22))
        tiempo_comp = f"A*: {tiempo_astar * 1000:.2f}ms  |  BFS: {tiempo_bfs * 1000:.2f}ms"
        screen.blit(font.render(tiempo_comp, True, (180, 180, 200)), (sx + 15, y_line + 44))
    else:
        y_line = y_info + 22
        if revelados_astar < total_expl_astar:
            info_line = f"Explorando: {revelados_astar}/{total_expl_astar}"
        else:
            info_line = f"Paso: {paso_astar + 1}/{total_astar if total_astar else 0}"
        screen.blit(font.render(info_line, True, (180, 180, 200)), (sx + 15, y_line))
        tiempo_line = f"Tiempo: {tiempo_astar * 1000:.2f}ms"
        screen.blit(font.render(tiempo_line, True, (180, 180, 200)), (sx + 15, y_line + 22))

    return btn1_rect, btn2_rect, btn3_rect
