from collections import deque

def wave_algorithm(maze, start, end):
    """Возвращает список координат пути от start до end или None."""
    h, w = len(maze), len(maze[0])
    dist = [[-1]*w for _ in range(h)]
    queue = deque()
    dist[start[1]][start[0]] = 0
    queue.append(start)
    directions = [(0,1),(0,-1),(1,0),(-1,0)]
    while queue:
        x, y = queue.popleft()
        if (x, y) == end:
            break
        for dx, dy in directions:
            nx, ny = x+dx, y+dy
            if 0 <= nx < w and 0 <= ny < h and maze[ny][nx] == 0 and dist[ny][nx] == -1:
                dist[ny][nx] = dist[y][x] + 1
                queue.append((nx, ny))
    if dist[end[1]][end[0]] == -1:
        return None
    # Восстанавливаем путь
    path = []
    x, y = end
    while (x, y) != start:
        path.append((x, y))
        for dx, dy in directions:
            nx, ny = x+dx, y+dy
            if 0 <= nx < w and 0 <= ny < h and dist[ny][nx] == dist[y][x] - 1:
                x, y = nx, ny
                break
    path.append(start)
    path.reverse()
    return path

def right_hand_rule(maze, start, end, step_by_step=False, delay_ms=500):
    """
    Генератор, возвращающий текущую позицию на каждом шаге.
    Если step_by_step=True, ждёт нажатия клавиши, иначе задержка delay_ms.
    """
    # Направления: 0=вправо, 1=вниз, 2=влево, 3=вверх
    # Для правила правой руки: если справа проход, повернуть направо и шагнуть; иначе если прямо проход – шагнуть; иначе повернуть налево.
    dirs = [(1,0), (0,1), (-1,0), (0,-1)]
    x, y = start
    # Определяем начальное направление: смотрим, куда ведёт проход из стартовой точки
    # Поскольку вход на границе, направление внутрь
    if y == 0: direction = 1  # вниз
    elif y == len(maze)-1: direction = 3  # вверх
    elif x == 0: direction = 0  # вправо
    else: direction = 2  # влево

    visited = set()
    while (x, y) != end:
        yield (x, y), direction
        # Проверяем клетку справа
        right_dir = (direction + 1) % 4
        dx, dy = dirs[right_dir]
        rx, ry = x+dx, y+dy
        if 0 <= rx < len(maze[0]) and 0 <= ry < len(maze) and maze[ry][rx] == 0:
            direction = right_dir
            x, y = rx, ry
        else:
            # Проверяем прямо
            dx, dy = dirs[direction]
            fx, fy = x+dx, y+dy
            if 0 <= fx < len(maze[0]) and 0 <= fy < len(maze) and maze[fy][fx] == 0:
                x, y = fx, fy
            else:
                # Поворачиваем налево (direction - 1)
                direction = (direction - 1) % 4
        # Для пошагового режима можно добавить ожидание через input(), но в GUI это будет отдельно
        # В GUI реализуем таймер/события
    yield (x, y), direction