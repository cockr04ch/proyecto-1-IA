from config import FILAS, COLUMNAS, META_POS, INICIO_POS
import random


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


def heuristica(nodo):
    return abs(nodo.fila - META_POS[0]) + abs(nodo.columna - META_POS[1])


def crear_matriz():
    return [[Nodo(f, c) for c in range(COLUMNAS)] for f in range(FILAS)]


def generar_obstaculos(matriz):
    for i in range(FILAS):
        for j in range(COLUMNAS):
            if random.random() < 0.3:
                matriz[i][j].caminable = False
    matriz[INICIO_POS[0]][INICIO_POS[1]].caminable = True
    matriz[META_POS[0]][META_POS[1]].caminable = True
    matriz[1][2].caminable = True
    matriz[2][1].caminable = True


def mapeo(matriz):
    inicio = matriz[INICIO_POS[0]][INICIO_POS[1]]
    meta = matriz[META_POS[0]][META_POS[1]]

    listaAbierta = []
    listaCerrada = []

    inicio.h = heuristica(inicio)
    inicio.f = inicio.h + inicio.g
    listaAbierta.append(inicio)

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

        for df, dc in direcciones:
            nueva_fila = nodo_actual.fila + df
            nueva_col = nodo_actual.columna + dc

            if 0 <= nueva_fila < FILAS and 0 <= nueva_col < COLUMNAS:
                vecino = matriz[nueva_fila][nueva_col]

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
