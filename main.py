import pygame
import sys
import time
from config import (
    NORMAL_FILAS, NORMAL_COLUMNAS, NORMAL_CELL_SIZE,
    NORMAL_WINDOW_WIDTH, NORMAL_WINDOW_HEIGHT, NORMAL_SIDEBAR_X,
    NORMAL_META, NORMAL_INICIO,
    COMP_FILAS, COMP_COLUMNAS, COMP_CELL_SIZE,
    COMP_WINDOW_WIDTH, COMP_WINDOW_HEIGHT, COMP_SIDEBAR_X,
    COMP_META, COMP_INICIO,
    COLOR_FONDO, FRAMES_POR_PASO, FPS,
)
from pathfinding import (
    crear_matriz, generar_obstaculos, mapeo, mapeo_bfs, reset_nodos,
)
from graphics import (
    init_pygame, load_sprites, draw_grid_normal,
    draw_comparison_view, draw_sidebar,
)


def regenerar_mapa(matriz, inicio_pos, meta_pos):
    for fila in matriz:
        for nodo in fila:
            nodo.caminable = True
            nodo.padre = None
            nodo.g = 0
            nodo.h = 0
            nodo.f = 0
    generar_obstaculos(matriz, inicio_pos, meta_pos)


def ejecutar_astar(matriz, inicio, meta):
    t0 = time.perf_counter()
    camino, explorados = mapeo(matriz, inicio, meta)
    t = time.perf_counter() - t0
    return camino, explorados, t


def ejecutar_bfs(matriz, inicio, meta):
    t0 = time.perf_counter()
    camino, explorados = mapeo_bfs(matriz, inicio, meta)
    t = time.perf_counter() - t0
    return camino, explorados, t


def calcular_batches(explorados_a, explorados_b, modo_comp):
    total_a = len(explorados_a) if explorados_a else 0
    target = FPS * 3 if total_a > 100 else FPS * 1
    batch_a = max(1, total_a // target) if total_a else 0
    if modo_comp:
        total_b = len(explorados_b) if explorados_b else 0
        target_b = FPS * 3 if total_b > 100 else FPS * 1
        batch_b = max(1, total_b // target_b) if total_b else 0
    else:
        batch_b = 0
    return batch_a, batch_b


def setup_normal():
    m = crear_matriz(NORMAL_FILAS, NORMAL_COLUMNAS)
    generar_obstaculos(m, NORMAL_INICIO, NORMAL_META)
    c, e, t = ejecutar_astar(m, NORMAL_INICIO, NORMAL_META)
    return m, c, e, t


def setup_comparacion():
    m = crear_matriz(COMP_FILAS, COMP_COLUMNAS)
    generar_obstaculos(m, COMP_INICIO, COMP_META)
    ca, ea, ta = ejecutar_astar(m, COMP_INICIO, COMP_META)
    reset_nodos(m)
    cb, eb, tb = ejecutar_bfs(m, COMP_INICIO, COMP_META)
    return m, ca, ea, ta, cb, eb, tb


def reiniciar_estado():
    return 0, 0, 0, 0


def main():
    modo_comparacion = False
    cell_size = NORMAL_CELL_SIZE
    ancho = NORMAL_WINDOW_WIDTH
    alto = NORMAL_WINDOW_HEIGHT
    sidebar_x = NORMAL_SIDEBAR_X
    inicio_pos = NORMAL_INICIO
    meta_pos = NORMAL_META

    matriz, camino_astar, explorados_astar, tiempo_astar = setup_normal()
    camino_bfs = None
    explorados_bfs = []
    tiempo_bfs = 0.0

    batch_a, batch_b = calcular_batches(explorados_astar, explorados_bfs, modo_comparacion)

    screen, clock, font, font_bold = init_pygame(ancho, alto)
    zombie_sprite, raider_frames, raider_idle = load_sprites(cell_size)

    paso_astar = 0
    paso_bfs = 0
    frame_anim = 0
    revelados_astar = 0
    revelados_bfs = 0
    contador_explora = 0
    contador_camina = 0

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                total_a = len(camino_astar) if camino_astar else 0
                total_b = len(camino_bfs) if camino_bfs else 0
                btn1_rect, btn2_rect, btn3_rect = draw_sidebar(
                    screen, font, mouse_pos,
                    paso_astar, total_a,
                    paso_bfs, total_b,
                    tiempo_astar, tiempo_bfs,
                    modo_comparacion, sidebar_x, alto,
                    revelados_astar, len(explorados_astar) if explorados_astar else 0,
                    revelados_bfs, len(explorados_bfs) if explorados_bfs else 0,
                )

                if btn1_rect.collidepoint(event.pos):
                    regenerar_mapa(matriz, inicio_pos, meta_pos)
                    if modo_comparacion:
                        camino_astar, explorados_astar, tiempo_astar = ejecutar_astar(
                            matriz, inicio_pos, meta_pos
                        )
                        reset_nodos(matriz)
                        camino_bfs, explorados_bfs, tiempo_bfs = ejecutar_bfs(
                            matriz, inicio_pos, meta_pos
                        )
                    else:
                        camino_astar, explorados_astar, tiempo_astar = ejecutar_astar(
                            matriz, inicio_pos, meta_pos
                        )
                    batch_a, batch_b = calcular_batches(
                        explorados_astar, explorados_bfs, modo_comparacion
                    )
                    paso_astar = paso_bfs = frame_anim = 0
                    revelados_astar = revelados_bfs = 0
                    contador_explora = contador_camina = 0

                elif btn2_rect.collidepoint(event.pos):
                    paso_astar = paso_bfs = frame_anim = 0
                    contador_explora = contador_camina = 0
                    if revelados_astar < len(explorados_astar):
                        revelados_astar = revelados_bfs = 0

                elif btn3_rect.collidepoint(event.pos):
                    modo_comparacion = not modo_comparacion
                    if modo_comparacion:
                        cell_size = COMP_CELL_SIZE
                        ancho = COMP_WINDOW_WIDTH
                        alto = COMP_WINDOW_HEIGHT
                        sidebar_x = COMP_SIDEBAR_X
                        inicio_pos = COMP_INICIO
                        meta_pos = COMP_META
                        matriz, camino_astar, explorados_astar, tiempo_astar, \
                            camino_bfs, explorados_bfs, tiempo_bfs = setup_comparacion()
                    else:
                        cell_size = NORMAL_CELL_SIZE
                        ancho = NORMAL_WINDOW_WIDTH
                        alto = NORMAL_WINDOW_HEIGHT
                        sidebar_x = NORMAL_SIDEBAR_X
                        inicio_pos = NORMAL_INICIO
                        meta_pos = NORMAL_META
                        camino_bfs = None
                        explorados_bfs = []
                        tiempo_bfs = 0.0
                        matriz, camino_astar, explorados_astar, tiempo_astar = setup_normal()
                    batch_a, batch_b = calcular_batches(
                        explorados_astar, explorados_bfs, modo_comparacion
                    )
                    screen = pygame.display.set_mode((ancho, alto))
                    zombie_sprite, raider_frames, raider_idle = load_sprites(cell_size)
                    paso_astar = paso_bfs = frame_anim = 0
                    revelados_astar = revelados_bfs = 0
                    contador_explora = contador_camina = 0

        total_expl_a = len(explorados_astar) if explorados_astar else 0
        total_expl_b = len(explorados_bfs) if explorados_bfs else 0
        expl_a_done = revelados_astar >= total_expl_a
        expl_b_done = revelados_bfs >= total_expl_b if modo_comparacion else True

        if not expl_a_done or not expl_b_done:
            contador_explora += 1
            if contador_explora >= 1:
                contador_explora = 0
                if not expl_a_done:
                    revelados_astar = min(total_expl_a, revelados_astar + batch_a)
                if modo_comparacion and not expl_b_done:
                    revelados_bfs = min(total_expl_b, revelados_bfs + batch_b)

        exploracion_terminada = expl_a_done and expl_b_done

        en_movimiento_a = (
            exploracion_terminada
            and camino_astar is not None
            and paso_astar < len(camino_astar) - 1
        )
        en_movimiento_b = (
            exploracion_terminada
            and modo_comparacion
            and camino_bfs is not None
            and paso_bfs < len(camino_bfs) - 1
        )

        if en_movimiento_a or en_movimiento_b:
            contador_camina += 1
            if contador_camina >= FRAMES_POR_PASO:
                contador_camina = 0
                if en_movimiento_a:
                    paso_astar += 1
                if en_movimiento_b:
                    paso_bfs += 1
                frame_anim = (frame_anim + 1) % 8

        screen.fill(COLOR_FONDO)

        if modo_comparacion:
            draw_comparison_view(
                screen, matriz, cell_size,
                camino_astar, explorados_astar, revelados_astar, paso_astar,
                camino_bfs, explorados_bfs, revelados_bfs, paso_bfs,
                zombie_sprite, raider_frames, frame_anim,
                frame_anim, raider_idle,
                font, font_bold, tiempo_astar, tiempo_bfs,
            )
        else:
            draw_grid_normal(
                screen, matriz, cell_size,
                camino_astar, explorados_astar, revelados_astar, paso_astar,
                zombie_sprite, raider_frames, frame_anim, raider_idle,
            )

        total_a = len(camino_astar) if camino_astar else 0
        total_b = len(camino_bfs) if camino_bfs else 0
        draw_sidebar(
            screen, font, mouse_pos,
            paso_astar, total_a,
            paso_bfs, total_b,
            tiempo_astar, tiempo_bfs,
            modo_comparacion, sidebar_x, alto,
            revelados_astar, total_expl_a,
            revelados_bfs, total_expl_b,
        )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
