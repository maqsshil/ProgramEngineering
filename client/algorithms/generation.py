import random
from .maze_utils import init_grid_for_generation

def recursive_backtracker(height, width, forbidden_node=None):
    grid = init_grid_for_generation(height, width)

    if forbidden_node:
        fx, fy = forbidden_node
        grid[fy][fx] = 1

    # список всех узлов
    nodes = [(x, y) for y in range(1, height-1, 2)
                       for x in range(1, width-1, 2)]

    if forbidden_node in nodes:
        nodes.remove(forbidden_node)

    start_x, start_y = random.choice(nodes)

    stack = [(start_x, start_y)]
    visited = set([(start_x, start_y)])

    grid[start_y][start_x] = 0

    while stack:
        x, y = stack[-1]

        neighbours = []
        for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in nodes and (nx, ny) not in visited:
                neighbours.append((nx, ny, dx//2, dy//2))

        if neighbours:
            nx, ny, dxw, dyw = random.choice(neighbours)
            grid[y + dyw][x + dxw] = 0
            grid[ny][nx] = 0
            visited.add((nx, ny))
            stack.append((nx, ny))
        else:
            stack.pop()

    # границы — стены
    for i in range(height):
        grid[i][0] = 1
        grid[i][width-1] = 1
    for j in range(width):
        grid[0][j] = 1
        grid[height-1][j] = 1

    return grid

def kruskal(height, width, forbidden_node=None):
    grid = init_grid_for_generation(height, width)

    if forbidden_node:
        fx, fy = forbidden_node
        grid[fy][fx] = 1

    cells = [(x, y) for y in range(1, height-1, 2)
                       for x in range(1, width-1, 2)]

    if forbidden_node in cells:
        cells.remove(forbidden_node)

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

    walls = []
    for (x, y) in cells:
        if (x+2, y) in cells:
            walls.append((x, y, x+2, y))
        if (x, y+2) in cells:
            walls.append((x, y, x, y+2))

    random.shuffle(walls)

    for (x1, y1, x2, y2) in walls:
        if union((x1, y1), (x2, y2)):
            grid[(y1+y2)//2][(x1+x2)//2] = 0
            grid[y1][x1] = 0
            grid[y2][x2] = 0

    for i in range(height):
        grid[i][0] = 1
        grid[i][width-1] = 1
    for j in range(width):
        grid[0][j] = 1
        grid[height-1][j] = 1

    return grid