def create_empty_maze(height, width):
    """Создаёт пустой лабиринт (все стены) с заданными размерами."""
    return [[1 for _ in range(width)] for _ in range(height)]

def init_grid_for_generation(height, width):
    """
    Для алгоритмов, работающих с клетками-проходами (нечётные координаты).
    Возвращает матрицу, где 0 - непосещённая клетка, 1 - стена.
    Но в процессе генерации проходы делаются из нулей.
    """
    # Начинаем с матрицы со стенами (1)
    grid = create_empty_maze(height, width)
    # Все клетки с нечётными индексами будут потенциальными проходами (пока 0)
    for i in range(1, height-1, 2):
        for j in range(1, width-1, 2):
            grid[i][j] = 0
    return grid
# algorithms/maze_utils.py
from collections import deque

def has_path(maze, start, end):
    """Проверяет, существует ли путь от start до end (BFS)."""
    h, w = len(maze), len(maze[0])
    visited = [[False]*w for _ in range(h)]
    q = deque([start])
    visited[start[1]][start[0]] = True
    dirs = [(0,1),(0,-1),(1,0),(-1,0)]
    while q:
        x, y = q.popleft()
        if (x, y) == end:
            return True
        for dx, dy in dirs:
            nx, ny = x+dx, y+dy
            if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx] and maze[ny][nx] == 0:
                visited[ny][nx] = True
                q.append((nx, ny))
    return False

def count_dead_ends(maze):
    """Возвращает количество тупиков (клеток-проходов, у которых ровно 1 сосед-проход)."""
    h, w = len(maze), len(maze[0])
    dead_ends = 0
    dirs = [(0,1),(0,-1),(1,0),(-1,0)]
    for y in range(h):
        for x in range(w):
            if maze[y][x] == 0:
                neighbors = 0
                for dx, dy in dirs:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < w and 0 <= ny < h and maze[ny][nx] == 0:
                        neighbors += 1
                if neighbors == 1:
                    dead_ends += 1
    return dead_ends

def has_isolated_areas(maze):
    """Проверяет, все ли проходимые клетки достижимы из стартовой позиции (вход)."""
    # Найдём первую попавшуюся проходимую клетку (вход)
    h, w = len(maze), len(maze[0])
    start = None
    for y in range(h):
        for x in range(w):
            if maze[y][x] == 0:
                start = (x, y)
                break
        if start:
            break
    if not start:
        return False  # нет проходов
    visited = [[False]*w for _ in range(h)]
    q = deque([start])
    visited[start[1]][start[0]] = True
    dirs = [(0,1),(0,-1),(1,0),(-1,0)]
    while q:
        x, y = q.popleft()
        for dx, dy in dirs:
            nx, ny = x+dx, y+dy
            if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx] and maze[ny][nx] == 0:
                visited[ny][nx] = True
                q.append((nx, ny))
    # Если есть непосещённая проходимая клетка – изолированная зона
    for y in range(h):
        for x in range(w):
            if maze[y][x] == 0 and not visited[y][x]:
                return True
    return False
def auto_place_entrance_exit(grid):
    """Автоматически расставляет вход и выход на периметре (не углы, не соседние)."""
    h = len(grid)
    w = len(grid[0])
    positions = []
    # верхняя и нижняя границы
    for x in range(1, w-1):
        positions.append((x, 0))
        positions.append((x, h-1))
    # левая и правая границы
    for y in range(1, h-1):
        positions.append((0, y))
        positions.append((w-1, y))
    import random
    random.shuffle(positions)
    entry = None
    exit_ = None
    for i in range(len(positions)):
        for j in range(i+1, len(positions)):
            p1 = positions[i]
            p2 = positions[j]
            # проверка, что не соседние (расстояние > 1)
            if abs(p1[0]-p2[0]) + abs(p1[1]-p2[1]) > 1:
                entry = p1
                exit_ = p2
                break
        if entry:
            break
    if entry is None:
        # fallback – берём первые две подходящие
        entry = positions[0]
        exit_ = positions[1]
    return entry, exit_