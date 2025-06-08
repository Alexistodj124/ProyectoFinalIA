import random

DIRECTIONS = [
    (-1, -1),  # UP-LEFT
    (-1, 0),   # UP
    (-1, 1),   # UP-RIGHT
    (0, -1),   # LEFT
    (0, 1),    # RIGHT
    (1, -1),   # DOWN-LEFT
    (1, 0),    # DOWN
    (1, 1)     # DOWN-RIGHT
]

def in_bounds(x, y):
    return 0 <= x < 8 and 0 <= y < 8

def valid_movements(board, player):
    opponent = -player
    valid_moves = []

    for x in range(8):
        for y in range(8):
            if board[x][y] != 0:
                continue

            for dx, dy in DIRECTIONS:
                i, j = x + dx, y + dy
                found_opponent = False

                while in_bounds(i, j) and board[i][j] == opponent:
                    i += dx
                    j += dy
                    found_opponent = True

                if found_opponent and in_bounds(i, j) and board[i][j] == player:
                    valid_moves.append((x, y))
                    break

    return valid_moves
 
# def ai_move(board, player):
#     import copy
#     DIRECTIONS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
#     def in_bounds(x, y): return 0 <= x < 8 and 0 <= y < 8
#     def valid_movements(b, p):
#         o = -p; moves = []
#         for x in range(8):
#             for y in range(8):
#                 if b[x][y] != 0: continue
#                 for dx, dy in DIRECTIONS:
#                     i, j = x + dx, y + dy; found = False
#                     while in_bounds(i,j) and b[i][j]==o: i+=dx; j+=dy; found=True
#                     if found and in_bounds(i,j) and b[i][j]==p:
#                         moves.append((x,y)); break
#         return moves
#     def simulate_move(b, x, y, p):
#         o = -p; b[x][y] = p
#         for dx, dy in DIRECTIONS:
#             i, j = x + dx, y + dy; flips = []
#             while in_bounds(i,j) and b[i][j]==o:
#                 flips.append((i,j)); i+=dx; j+=dy
#             if in_bounds(i,j) and b[i][j]==p:
#                 for fx,fy in flips: b[fx][fy]=p
#     def evaluate(b, p):
#         o = -p; s = 0
#         corners=[(0,0),(0,7),(7,0),(7,7)]
#         x_squares=[(1,1),(1,6),(6,1),(6,6)]
#         near_corners=[(0,1),(1,0),(0,6),(1,7),(6,0),(7,1),(6,7),(7,6)]
#         my, op = len(valid_movements(b, p)), len(valid_movements(b, o))
#         for x in range(8):
#             for y in range(8):
#                 if b[x][y]==p:
#                     s+=1
#                     if (x,y) in corners: s+=25
#                     elif (x,y) in x_squares: s-=12
#                     elif (x,y) in near_corners: s-=8
#                     elif x in [0,7] or y in [0,7]: s+=4
#                 elif b[x][y]==o:
#                     s-=1
#                     if (x,y) in corners: s-=25
#                     elif (x,y) in x_squares: s+=12
#                     elif (x,y) in near_corners: s+=8
#                     elif x in [0,7] or y in [0,7]: s-=4
#         s += 3*(my - op)
#         return s
#     def minimax(b, p, d, m, a, beta):
#         vm = valid_movements(b,p)
#         if d==0 or not vm: return evaluate(b,m),None
#         bm = None
#         if p==m:
#             max_eval = float('-inf')
#             for move in vm:
#                 new = copy.deepcopy(b)
#                 simulate_move(new, move[0], move[1], p)
#                 e,_ = minimax(new,-p,d-1,m,a,beta)
#                 if e > max_eval: max_eval = e; bm = move
#                 a = max(a,e); 
#                 if beta<=a: break
#             return max_eval, bm
#         else:
#             min_eval = float('inf')
#             for move in vm:
#                 new = copy.deepcopy(b)
#                 simulate_move(new, move[0], move[1], p)
#                 e,_ = minimax(new,-p,d-1,m,a,beta)
#                 if e < min_eval: min_eval = e; bm = move
#                 beta = min(beta,e)
#                 if beta<=a: break
#             return min_eval, bm
#     _, move = minimax(board, player, 3, player, float('-inf'), float('inf'))
#     return move

import time
import copy

# =====================================================
# Constantes y estructuras de datos
# =====================================================
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              ( 0, -1),          ( 0, 1),
              ( 1, -1), ( 1, 0), ( 1, 1)]

CORNERS    = [(0, 0), (0, 7), (7, 0), (7, 7)]
X_SQUARES  = [(1, 1), (1, 6), (6, 1), (6, 6)]
C_SQUARES  = [(0, 1), (1, 0), (0, 6), (1, 7),
              (6, 0), (7, 1), (6, 7), (7, 6)]
EDGES      = [(0, y) for y in range(8)] + [(7, y) for y in range(8)] + \
             [(x, 0) for x in range(8)] + [(x, 7) for x in range(8)]

# Pesos para la función de evaluación
WEIGHT_CORNER        = 1000
WEIGHT_NEAR_CORNER   = -200
WEIGHT_STABLE_DISC   = 250
WEIGHT_OPP_STABLE    = -250
WEIGHT_EDGE_DISC     = 50
WEIGHT_OPP_EDGE      = -50
WEIGHT_FRONTIER_DISC = -20
WEIGHT_OPP_FRONTIER  = 20
WEIGHT_MOBILITY      = 15
WEIGHT_OPP_MOBILITY  = -15

# =====================================================
# Funciones básicas
# =====================================================
def in_bounds(x, y):
    return 0 <= x < 8 and 0 <= y < 8

def valid_movements(board, player):
    """
    Devuelve lista de casillas (x, y) donde 'player' puede mover en 'board'.
    """
    o = -player
    moves = []
    for x in range(8):
        for y in range(8):
            if board[x][y] != 0:
                continue
            for dx, dy in DIRECTIONS:
                i, j = x + dx, y + dy
                found = False
                while in_bounds(i, j) and board[i][j] == o:
                    i += dx; j += dy; found = True
                if found and in_bounds(i, j) and board[i][j] == player:
                    moves.append((x, y))
                    break
    return moves

def simulate_move(board, x, y, player):
    """
    Hace el movimiento (x, y) para 'player' en 'board', volteando los discos correspondientes.
    """
    o = -player
    board[x][y] = player
    for dx, dy in DIRECTIONS:
        i, j = x + dx, y + dy
        flips = []
        while in_bounds(i, j) and board[i][j] == o:
            flips.append((i, j))
            i += dx; j += dy
        if in_bounds(i, j) and board[i][j] == player:
            for fx, fy in flips:
                board[fx][fy] = player

# =====================================================
# Conteo de discos estables (Chapter 2) 
# =====================================================
def count_stable_discs(board, player):
    stable = [[False]*8 for _ in range(8)]
    # Marcar esquinas ocupadas
    for cx, cy in CORNERS:
        if board[cx][cy] == player:
            stable[cx][cy] = True

    changed = True
    while changed:
        changed = False
        for x in range(8):
            for y in range(8):
                if board[x][y] != player or stable[x][y]:
                    continue
                # Si desde (x,y) existe alguna línea ortogonal/vertical que
                # termine en disco estable propio sin interrupciones, lo marcamos estable.
                for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                    i, j = x, y
                    linea_estable = False
                    while True:
                        i += dx; j += dy
                        if not in_bounds(i, j) or not stable[i][j]:
                            linea_estable = False
                            break
                        if board[i][j] == player:
                            linea_estable = True
                        else:
                            linea_estable = False
                            break
                    if linea_estable:
                        stable[x][y] = True
                        changed = True
                        break

    return sum(1 for i in range(8) for j in range(8) if stable[i][j])

# =====================================================
# Conteo de discos de frontera (Chapter 3) 
# =====================================================
def count_frontier_discs(board, player):
    frontier = 0
    for x in range(8):
        for y in range(8):
            if board[x][y] != player:
                continue
            for dx, dy in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if in_bounds(nx, ny) and board[nx][ny] == 0:
                    frontier += 1
                    break
    return frontier

# =====================================================
# Función de evaluación
# =====================================================
def evaluate(board, player):
    """
    Combina:
      • Corner occupancy
      • Discos estables (Chapter 2) 
      • Discos de frontera (Chapter 3) 
      • Discos en bordes y peligro de X/C-squares
      • Movilidad
      • En el final de partida (<10 vacíos), conteo de discos directo (Chapter 8)
    """
    o = -player
    empty_squares = sum(1 for i in range(8) for j in range(8) if board[i][j] == 0)

    # Determinar fase del juego
    if empty_squares > 40:
        phase = 'early'
    elif empty_squares > 10:
        phase = 'mid'
    else:
        phase = 'end'

    score = 0

    # 1) Esquinas
    for (x, y) in CORNERS:
        if board[x][y] == player:
            score += WEIGHT_CORNER
        elif board[x][y] == o:
            score -= WEIGHT_CORNER

    # 2) Discos estables
    stable_my  = count_stable_discs(board, player)
    stable_opp = count_stable_discs(board, o)
    score += WEIGHT_STABLE_DISC * stable_my
    score += WEIGHT_OPP_STABLE * stable_opp

    # 3) Discos de frontera
    frontier_my  = count_frontier_discs(board, player)
    frontier_opp = count_frontier_discs(board, o)
    score += WEIGHT_FRONTIER_DISC * frontier_my
    score += WEIGHT_OPP_FRONTIER * frontier_opp

    # 4) Borde seguro y penalizaciones de X/C-squares
    for x in range(8):
        for y in range(8):
            if board[x][y] == player:
                if (x, y) in EDGES and (x, y) not in CORNERS and (x, y) not in X_SQUARES + C_SQUARES:
                    score += WEIGHT_EDGE_DISC
                if (x, y) in X_SQUARES + C_SQUARES:
                    # Verificar si está “sujeto” por una cadena propia
                    safe = False
                    for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                        i, j = x, y
                        cadena = True
                        while True:
                            i += dx; j += dy
                            if not in_bounds(i, j) or board[i][j] != player:
                                cadena = False
                                break
                            if (i, j) in CORNERS or (i, j) in EDGES:
                                cadena = True
                                break
                        if cadena:
                            safe = True
                            break
                    if not safe:
                        score += WEIGHT_NEAR_CORNER

            elif board[x][y] == o:
                if (x, y) in EDGES and (x, y) not in CORNERS and (x, y) not in X_SQUARES + C_SQUARES:
                    score += WEIGHT_OPP_EDGE
                if (x, y) in X_SQUARES + C_SQUARES:
                    safe_opp = False
                    for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                        i, j = x, y
                        cadena = True
                        while True:
                            i += dx; j += dy
                            if not in_bounds(i, j) or board[i][j] != o:
                                cadena = False
                                break
                            if (i, j) in CORNERS or (i, j) in EDGES:
                                cadena = True
                                break
                        if cadena:
                            safe_opp = True
                            break
                    if not safe_opp:
                        score -= WEIGHT_NEAR_CORNER

    # 5) Movilidad
    moves_my  = len(valid_movements(board, player))
    moves_opp = len(valid_movements(board, o))
    score += WEIGHT_MOBILITY * moves_my
    score += WEIGHT_OPP_MOBILITY * moves_opp

    # 6) Final de partida: conteo directo y paridad
    if phase == 'end':
        discs_my  = sum(1 for i in range(8) for j in range(8) if board[i][j] == player)
        discs_opp = sum(1 for i in range(8) for j in range(8) if board[i][j] == o)
        score += (discs_my - discs_opp) * 100

    # Para debug: mostrar fase
    # (En tu salida de torneo salía “Game phase: opening”,
    #  pero aquí la variable es 'early'/'mid'/'end')
    # Puedes comentarlo si no quieres imprimirlo cada vez:
    #
    # if phase == 'early':
    #     print("Game phase: opening")
    # elif phase == 'mid':
    #     print("Game phase: midgame")
    # else:
    #     print("Game phase: endgame")

    return score

# =====================================================
# Minimax con α-β, ordenación de movimientos e Iterative Deepening
# =====================================================
def minimax(root_board, player, max_depth, time_limit):
    """
    Busca la mejor jugada para 'player' en 'root_board' usando:
      • Recorte Alfa-Beta
      • Ordenación de moves (Corners → Edges → demás)
      • Iterative deepening (hasta max_depth o hasta que se agote time_limit)
      • Imprime para debug los resultados de cada profundidad (Depth, Score, Move, Time)
    """
    # 1) Definir root_player desde el principio
    root_player = player

    best_move = None
    best_value = float('-inf') if player == root_player else float('inf')

    # 2) Definir search con cierre sobre root_player
    def search(board, current_player, depth, alpha, beta):
        nonlocal best_move, best_value

        # Chequear límite de tiempo
        if time.time() > time_limit:
            return evaluate(board, root_player), None

        legal = valid_movements(board, current_player)
        if depth == 0 or not legal:
            return evaluate(board, root_player), None

        # Ordenar movimientos: 0=corner, 1=edge, 2=resto
        def move_key(m):
            x, y = m
            if (x, y) in CORNERS:
                return 0
            if (x, y) in EDGES:
                return 1
            return 2

        legal.sort(key=move_key)

        best_local_move = None
        if current_player == root_player:
            value = float('-inf')
            for mv in legal:
                if time.time() > time_limit:
                    break
                new_board = copy.deepcopy(board)
                simulate_move(new_board, mv[0], mv[1], current_player)
                v, _ = search(new_board, -current_player, depth - 1, alpha, beta)
                if v > value:
                    value = v
                    best_local_move = mv
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value, best_local_move
        else:
            value = float('inf')
            for mv in legal:
                if time.time() > time_limit:
                    break
                new_board = copy.deepcopy(board)
                simulate_move(new_board, mv[0], mv[1], current_player)
                v, _ = search(new_board, -current_player, depth - 1, alpha, beta)
                if v < value:
                    value = v
                    best_local_move = mv
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value, best_local_move

    # 3) Iterative Deepening
    depths_completed = []
    total_start = time.time()

    for depth in range(1, max_depth + 1):
        if time.time() > time_limit:
            break

        depth_start = time.time()
        val, mv = search(root_board, player, depth, float('-inf'), float('inf'))
        depth_time = time.time() - depth_start

        # Solo guardamos si no nos pasamos del límite en esta iteración
        if time.time() <= time_limit and mv is not None:
            best_value, best_move = val, mv
            depths_completed.append(depth)
            # Impresión de debug (igual que en tu output de torneo)
            # print(f"Depth {depth}: Score={round(val, 1)}, Move={mv}, Time={round(depth_time, 3)}s")
        else:
            break

    total_time = time.time() - total_start
    # print(f"Estimated next iteration would exceed time limit, stopping at depth {depth}")
    # print(f"Final decision: Move={best_move}, Depths completed={depths_completed}, Total time={round(total_time, 3)}s")

    return best_value, best_move

# =====================================================
# Función principal ai_move
# =====================================================
def ai_move(board, player):
    """
    Llama a minimax con un límite de ~3 segundos por movimiento.
    """
    start_time = time.time()
    time_limit = start_time + 2.85

    # Profundidad máxima tentativa 6 (se detendrá antes si se agota el tiempo)
    _, best_mv = minimax(board, player, max_depth=6, time_limit=time_limit)
    return best_mv
