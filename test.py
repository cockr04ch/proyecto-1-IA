import pygame, sys, random
# configuraciones del jueguito
# g distanbia desde el nodo inicial al nodo actual
# h distancia desde el nodo actual al nodo final
# f = g + h suma de costos 
FILAS = 10
COLUMNAS = 10   

class Nodo:
    def __init__(self, fila, columna):
        self.fila = fila
        self.columna = columna
        self.posicion = (fila, columna)
        
        # Estado de la celda (1 = Libre, 0 = Obstáculo)
        self.caminable = True 
        
        # Variables para el algoritmo A*
        self.padre = None
        self.g = 0
        self.h = 0
        self.f = 0


matriz = [[Nodo(f, c) for c in range(COLUMNAS)] for f in range(FILAS)]

def mapeo(matriz):
    listaAbierta = []
    listaCerrada = []
    
    comienzo = matriz[0][0]
    meta = matriz[9][9]  # CORREGIDO: Buscamos en 'matriz'
    
    comienzo.h = heuristica(comienzo)
    comienzo.f = comienzo.h + comienzo.g
    listaAbierta.append(comienzo)

    while listaAbierta:
        # PASO 1: Encontrar el nodo con el costo F más bajo
        nodo_actual = listaAbierta[0]
        for nodo in listaAbierta:
            if nodo.f < nodo_actual.f:  # CORREGIDO: Agregamos el 'if'
                nodo_actual = nodo      # CORREGIDO: Va dentro del if

        # CORREGIDO: Estas líneas van dentro del 'while' con su sangría correcta
        listaAbierta.remove(nodo_actual)  # Sacamos de la abierta
        listaCerrada.append(nodo_actual)  # Metemos a la cerrada

        # PASO 2: ¿Llegamos a la meta? (¡Esto te faltaba!)
        if nodo_actual == meta:
            print("¡Camino encontrado!")
            camino = []
            actual = nodo_actual
            while actual is not None:
                camino.append(actual.posicion)
                actual = actual.padre
            return camino[::-1] # Retorna el camino del inicio al fin

        # PASO 3: Evaluar vecinos
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for VariableBusqueda, VariableBusqueda2 in direcciones:
            nuevaPos = nodo_actual.fila + VariableBusqueda
            nuevaPos2 = nodo_actual.columna + VariableBusqueda2

            # CORREGIDO: Usamos '<' para COLUMNAS
            if 0 <= nuevaPos < FILAS and 0 <= nuevaPos2 < COLUMNAS:
                vecino = matriz[nuevaPos][nuevaPos2]

                if not vecino.caminable or vecino in listaCerrada:
                    continue
                
                # --- CONTINUACIÓN DEL ALGORITMO (PASO 4) ---
                # Calculamos el posible costo G desde el nodo actual
                posible_g = nodo_actual.g + 1
                
                # Si el vecino no ha sido descubierto todavía
                if vecino not in listaAbierta:
                    vecino.padre = nodo_actual
                    vecino.g = posible_g
                    vecino.h = heuristica(vecino)
                    vecino.f = vecino.g + vecino.h
                    listaAbierta.append(vecino) # Lo agendamos para evaluar después
                
                # Si ya lo habíamos visto, pero descubrimos una ruta más barata
                elif posible_g < vecino.g:
                    vecino.padre = nodo_actual
                    vecino.g = posible_g
                    vecino.f = vecino.g + vecino.h

    print("No se encontró un camino posible.")
    return None


def heuristica(nodo_actual):
    # Distancia Manhattan
    return abs(nodo_actual.fila -9 ) + abs(nodo_actual.columna - 9)

def generar_obstaculos(matriz):
    for i in range(FILAS):
        for j in range(COLUMNAS):
            if random.random() < 0.3:  # 20% de probabilidad de ser un obstáculo
                matriz[i][j].caminable = False
    
    matriz[0][0].caminable = True  # Asegurar que el nodo de inicio sea caminable
    matriz[9][9].caminable = True
    matriz[1][2].caminable = True
    matriz[2][1].caminable = True 


# 1. Generamos los obstáculos en la matriz (esto ya lo tienes)
generar_obstaculos(matriz)

# 2. PROBAMOS EL ALGORITMO (Agrega estas líneas aquí)
print("Buscando el camino más corto...")
camino_final = mapeo(matriz)

print("\n--- RESULTADO DE LA BÚSQUEDA ---")
print(camino_final)
print("--------------------------------\n")

# 3. Inicializas Pygame (esto ya lo tienes)
pygame.init()
screen = pygame.display.set_mode((400, 300))

# Tu bucle principal de Pygame...
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

