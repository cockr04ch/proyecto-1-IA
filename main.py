import pygame
import sys
from config import COLOR_FONDO, FRAMES_POR_PASO, FPS
from pathfinding import crear_matriz, generar_obstaculos, mapeo
from graphics import (
    init_pygame, load_sprites, draw_grid,
    draw_character, draw_info, draw_sidebar,
)


def reiniciar_animacion():
    return 0, 0, 0


def regenerar_mapa(matriz):
    for f in range(len(matriz)):
        for c in range(len(matriz[0])):
            matriz[f][c].caminable = True
            matriz[f][c].padre = None
            matriz[f][c].g = 0
            matriz[f][c].h = 0
            matriz[f][c].f = 0

    generar_obstaculos(matriz)
    camino = mapeo(matriz)
    return camino


def main():
    matriz = crear_matriz()
    generar_obstaculos(matriz)
    camino = mapeo(matriz)

    screen, clock, font = init_pygame()
    zombie_sprite, raider_frames, raider_idle = load_sprites()

    paso_actual = 0
    frame_anim = 0
    contador_anim = 0
    en_movimiento = camino is not None and len(camino) > 1

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                btn1_rect, btn2_rect = draw_sidebar(
                    screen, font, mouse_pos, paso_actual,
                    len(camino) if camino else 0,
                )
                if btn1_rect.collidepoint(event.pos):
                    camino = regenerar_mapa(matriz)
                    paso_actual, frame_anim, contador_anim = reiniciar_animacion()
                    en_movimiento = camino is not None and len(camino) > 1

                elif btn2_rect.collidepoint(event.pos):
                    paso_actual, frame_anim, contador_anim = reiniciar_animacion()

        if en_movimiento and paso_actual < len(camino) - 1:
            contador_anim += 1
            if contador_anim >= FRAMES_POR_PASO:
                contador_anim = 0
                paso_actual += 1
                frame_anim = (frame_anim + 1) % 8

        screen.fill(COLOR_FONDO)
        draw_grid(screen, matriz, camino, paso_actual, zombie_sprite)
        draw_character(screen, camino, paso_actual, raider_frames, frame_anim, raider_idle)
        draw_info(screen, font, camino, paso_actual)
        draw_sidebar(
            screen, font, mouse_pos, paso_actual,
            len(camino) if camino else 0,
        )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
