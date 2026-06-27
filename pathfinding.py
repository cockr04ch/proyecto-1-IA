import random


class Nodo:
    """Representa una celda individual dentro de la cuadricula del mapa."""

    def __init__(self, fila, columna):
        """Inicializa un nodo con su posicion (fila, columna) y los atributos
        necesarios para los algoritmos de busqueda: g (coste real), h (heuristica),
        f (coste total), padre (rastro del camino) y caminable (true si no es obstaculo)."""
        self.fila = fila
        self.columna = columna
        self.posicion = (fila, columna)
        self.caminable = True
        self.padre = None
        self.g = 0
        self.h = 0
        self.f = 0


def heuristica(nodo, meta_pos):
    """Distancia Manhattan entre un nodo y la posicion meta.
    Se usa como heuristica admisible en A*."""
    return abs(nodo.fila - meta_pos[0]) + abs(nodo.columna - meta_pos[1])


def crear_matriz(filas, columnas):
    """Crea una cuadricula de nodos con las dimensiones dadas.
    Todos los nodos comienzan siendo caminables."""
    return [[Nodo(f, c) for c in range(columnas)] for f in range(filas)]


def generar_obstaculos(matriz, inicio_pos, meta_pos):
    """Asigna el 30% de las celdas como no caminables de forma aleatoria.
    Garantiza que la casilla de inicio, la meta y sus cuatro vecinos
    inmediatos permanezcan caminables."""
    filas = len(matriz)
    columnas = len(matriz[0])
    for i in range(filas):
        for j in range(columnas):
            if random.random() < 0.3:
                matriz[i][j].caminable = False
    matriz[inicio_pos[0]][inicio_pos[1]].caminable = True
    matriz[meta_pos[0]][meta_pos[1]].caminable = True
    for df, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ni, nj = inicio_pos[0] + df, inicio_pos[1] + dc
        if 0 <= ni < filas and 0 <= nj < columnas:
            matriz[ni][nj].caminable = True
        ni, nj = meta_pos[0] + df, meta_pos[1] + dc
        if 0 <= ni < filas and 0 <= nj < columnas:
            matriz[ni][nj].caminable = True


def reset_nodos(matriz):
    """Reinicia los valores de busqueda (padre, g, h, f) de todos los nodos
    sin modificar su estado caminable. Util antes de re-ejecutar un algoritmo."""
    for fila in matriz:
        for nodo in fila:
            nodo.padre = None
            nodo.g = 0
            nodo.h = 0
            nodo.f = 0


def mapeo(matriz, inicio_pos, meta_pos):
    """Algoritmo A* (A-Star). Busca el camino de menor coste desde inicio_pos
    hasta meta_pos usando la heuristica Manhattan. Retorna una tupla
    (camino, explorados): camino es la lista de posiciones ordenada desde
    inicio a meta, y explorados la lista de todos los nodos evaluados.
    Si no existe camino factible, retorna (None, explorados)."""
    filas = len(matriz)
    columnas = len(matriz[0])
    inicio = matriz[inicio_pos[0]][inicio_pos[1]]
    meta = matriz[meta_pos[0]][meta_pos[1]]

    listaAbierta = []
    listaCerrada = []

    inicio.h = heuristica(inicio, meta_pos)
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
            return camino[::-1], [n.posicion for n in listaCerrada]

        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for df, dc in direcciones:
            nueva_fila = nodo_actual.fila + df
            nueva_col = nodo_actual.columna + dc

            if 0 <= nueva_fila < filas and 0 <= nueva_col < columnas:
                vecino = matriz[nueva_fila][nueva_col]

                if not vecino.caminable or vecino in listaCerrada:
                    continue

                posible_g = nodo_actual.g + 1

                if vecino not in listaAbierta:
                    vecino.padre = nodo_actual
                    vecino.g = posible_g
                    vecino.h = heuristica(vecino, meta_pos)
                    vecino.f = vecino.g + vecino.h
                    listaAbierta.append(vecino)

                elif posible_g < vecino.g:
                    vecino.padre = nodo_actual
                    vecino.g = posible_g
                    vecino.f = vecino.g + vecino.h

    return None, [n.posicion for n in listaCerrada]


def mapeo_bfs(matriz, inicio_pos, meta_pos):
    """Algoritmo BFS (Breadth-First Search). Busca el camino desde inicio_pos
    hasta meta_pos explorando por niveles (anchura). Retorna una tupla
    (camino, explorados). Si no existe camino factible, retorna (None, explorados)."""
    filas = len(matriz)
    columnas = len(matriz[0])
    inicio = matriz[inicio_pos[0]][inicio_pos[1]]
    meta = matriz[meta_pos[0]][meta_pos[1]]

    cola = [inicio]
    visitados = []  # lista, no set - igual que A* usa listaCerrada (O(n) en in)
    explorados = []
    inicio.padre = None
    visitados.append(inicio)

    while cola:
        nodo_actual = cola.pop(0)
        explorados.append(nodo_actual.posicion)

        if nodo_actual == meta:
            camino = []
            actual = nodo_actual
            while actual is not None:
                camino.append(actual.posicion)
                actual = actual.padre
            return camino[::-1], explorados

        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for df, dc in direcciones:
            nueva_fila = nodo_actual.fila + df
            nueva_col = nodo_actual.columna + dc

            if 0 <= nueva_fila < filas and 0 <= nueva_col < columnas:
                vecino = matriz[nueva_fila][nueva_col]

                if vecino.caminable and vecino not in visitados:  # O(n), igual que A*
                    visitados.append(vecino)
                    vecino.padre = nodo_actual
                    cola.append(vecino)

    return None, explorados
