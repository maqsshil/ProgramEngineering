import random
from .maze_utils import init_grid_for_generation

def recursive_backtracker(height, width):
    """Генерация лабиринта методом рекурсивного бэктрекинга."""
    grid = init_grid_for_generation(height, width)
    # Начинаем с случайной клетки с нечётными координатами
    start_x = random.randrange(1, width, 2)
    start_y = random.randrange(1, height, 2)
    stack = [(start_x, start_y)]
    visited = set()
    visited.add((start_x, start_y))
    grid[start_y][start_x] = 0  # проход

    while stack:
        x, y = stack[-1]
        # Соседи через 2 клетки (up, down, left, right)
        neighbours = []
        for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
            nx, ny = x + dx, y + dy
            if 0 < nx < width-1 and 0 < ny < height-1 and (nx, ny) not in visited:
                neighbours.append((nx, ny, dx//2, dy//2))
        if neighbours:
            nx, ny, dxw, dyw = random.choice(neighbours)
            # Убираем стену между текущей и выбранной клеткой
            wall_x, wall_y = x + dxw, y + dyw
            grid[wall_y][wall_x] = 0
            grid[ny][nx] = 0
            visited.add((nx, ny))
            stack.append((nx, ny))
        else:
            stack.pop()
    # Гарантируем, что границы остаются стенами (кроме входа/выхода – позже)
    for i in range(height):
        grid[i][0] = 1
        grid[i][width-1] = 1
    for j in range(width):
        grid[0][j] = 1
        grid[height-1][j] = 1
    return grid
def kruskal(height, width):
    grid = init_grid_for_generation(height, width)
    # Список клеток-проходов (нечётные координаты)
    cells = []
    for i in range(1, height-1, 2):
        for j in range(1, width-1, 2):
            cells.append((j, i))  # x, y
    parent = {cell: cell for cell in cells}
    def find(cell):
        while parent[cell] != cell:
            parent[cell] = parent[parent[cell]]
            cell = parent[cell]
        return cell
    def union(c1, c2):
        p1, p2 = find(c1), find(c2)
        if p1 != p2:
            parent[p2] = p1
            return True
        return False

    # Собираем все возможные стены между клетками-проходами
    walls = []
    for (x, y) in cells:
        # правый сосед
        if x + 2 < width-1:
            nx, ny = x+2, y
            walls.append((x, y, nx, ny))
        # нижний сосед
        if y + 2 < height-1:
            nx, ny = x, y+2
            walls.append((x, y, nx, ny))
    random.shuffle(walls)

    for (x1, y1, x2, y2) in walls:
        if union((x1, y1), (x2, y2)):
            # убираем стену между ними
            wall_x = (x1 + x2)//2
            wall_y = (y1 + y2)//2
            grid[wall_y][wall_x] = 0
            grid[y1][x1] = 0
            grid[y2][x2] = 0
    # Границы
    for i in range(height):
        grid[i][0] = 1
        grid[i][width-1] = 1
    for j in range(width):
        grid[0][j] = 1
        grid[height-1][j] = 1
    return grid
def auto_place_entrance_exit(grid):
    h = len(grid)
    w = len(grid[0])
    # Собираем возможные позиции на периметре (не углы, и чтобы клетка была проходом или стеной? По условию: вход/выход на месте стены, затем пробиваем)
    # Но по прототипу – вход и выход ставятся на граничных стенах, которые потом становятся проходами.
    # Сначала выбираем стороны.
    positions = []
    # Верхняя и нижняя граница (y=0 или y=h-1), x от 1 до w-2
    for x in range(1, w-1):
        positions.append((x, 0))
        positions.append((x, h-1))
    # Левая и правая граница (x=0 или x=w-1), y от 1 до h-2
    for y in range(1, h-1):
        positions.append((0, y))
        positions.append((w-1, y))
    random.shuffle(positions)
    # Выбираем позиции входа и выхода
    entry = None
    exit_ = None
    for i in range(len(positions)):
        for j in range(i+1, len(positions)):
            e1 = positions[i]
            e2 = positions[j]
            # Проверка: не совпадают, не соседние (манхэттенское расстояние > 1)
            if abs(e1[0]-e2[0]) + abs(e1[1]-e2[1]) > 1:
                entry = e1
                exit_ = e2
                break
        if entry:
            break
    # Пробиваем стены в этих позициях
    grid[entry[1]][entry[0]] = 0
    grid[exit_[1]][exit_[0]] = 0
    return entry, exit_