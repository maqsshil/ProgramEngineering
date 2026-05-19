from collections import deque

def wave_algorithm(maze, start, end):
    h, w = len(maze), len(maze[0])
    dist = [[-1]*w for _ in range(h)]
    queue = deque()

    dist[start[1]][start[0]] = 0
    queue.append(start)

    directions = [(0,1),(0,-1),(1,0),(-1,0)]

    while queue:
        x, y = queue.popleft()

        for dx, dy in directions:
            nx, ny = x+dx, y+dy

            if 0 <= nx < w and 0 <= ny < h:
                if maze[ny][nx] == 0 and dist[ny][nx] == -1:
                    dist[ny][nx] = dist[y][x] + 1
                    queue.append((nx, ny))

    if dist[end[1]][end[0]] == -1:
        return None, None

    # восстановление пути
    path = []
    x, y = end

    while (x, y) != start:
        path.append((x, y))
        for dx, dy in directions:
            nx, ny = x+dx, y+dy
            if 0 <= nx < w and 0 <= ny < h:
                if dist[ny][nx] == dist[y][x] - 1:
                    x, y = nx, ny
                    break

    path.append(start)
    path.reverse()

    return dist, path

def right_hand_rule(maze, start, end):
    dirs = [(1,0), (0,1), (-1,0), (0,-1)]  # R, D, L, U

    x, y = start

    # направление внутрь лабиринта
    if y == 0:
        direction = 1
    elif y == len(maze)-1:
        direction = 3
    elif x == 0:
        direction = 0
    else:
        direction = 2

    yield (x, y), direction

    while (x, y) != end:

        # проверяем максимум 4 поворота
        for _ in range(4):

            # сначала проверяем справа
            right_dir = (direction + 1) % 4
            dx, dy = dirs[right_dir]
            rx, ry = x + dx, y + dy

            if 0 <= rx < len(maze[0]) and 0 <= ry < len(maze) and maze[ry][rx] == 0:
                direction = right_dir
                x, y = rx, ry
                break

            # иначе проверяем прямо
            dx, dy = dirs[direction]
            fx, fy = x + dx, y + dy

            if 0 <= fx < len(maze[0]) and 0 <= fy < len(maze) and maze[fy][fx] == 0:
                x, y = fx, fy
                break

            # иначе поворачиваем налево
            direction = (direction - 1) % 4

        yield (x, y), direction