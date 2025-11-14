#  pip install pygame

# pip install numpy




import pygame
import random
import heapq

pygame.init()

# ----------- Window -----------
WIDTH, HEIGHT = 900, 700
TILE = 40
ROWS, COLS = HEIGHT // TILE, WIDTH // TILE
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spy AI Game – Slow Stealth Edition")

clock = pygame.time.Clock()

# ----------- Colors -----------
BLACK = (0,0,0)
GRAY = (60,60,60)
BLUE = (0,120,255)
RED = (255,50,50)
YELLOW = (255,255,0)
CYAN = (0,255,255)

# ----------- Map -----------
def generate_map():
    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    for r in range(ROWS):
        for c in range(COLS):
            if random.random() < 0.13:
                grid[r][c] = 1
    # Clear spawn area
    for rr in range(5):
        for cc in range(5):
            grid[rr][cc] = 0
    return grid

grid = generate_map()

# ----------- Player -----------
player_tile = [2, 2]       # tile position
player_pos = [2.0, 2.0]    # smooth float position
player_speed = 0.06       # slower movement

# ----------- Treasure -----------
def place_treasure():
    while True:
        r = random.randint(1, ROWS-2)
        c = random.randint(1, COLS-2)
        if grid[r][c] == 0:
            return [c, r]

treasure = place_treasure()
treasure_collected = False

# ----------- Enemies -----------
def create_enemy():
    while True:
        r = random.randint(0, ROWS-1)
        c = random.randint(0, COLS-1)
        if grid[r][c] == 0 and [c, r] != player_tile:
            return {"pos": [c, r], "fpos": [float(c), float(r)], "path": [], "stun_timer": 0}

enemies = [create_enemy() for _ in range(5)]

# ----------- Pathfinding -----------
def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar(start, goal):
    neighbors = [(1,0),(-1,0),(0,1),(0,-1)]
    pq = []
    heapq.heappush(pq, (0, start))
    came_from = {}
    cost = {start: 0}

    while pq:
        _, current = heapq.heappop(pq)
        if current == goal: break
        for dx, dy in neighbors:
            nxt = (current[0]+dx, current[1]+dy)
            if 0 <= nxt[0] < COLS and 0 <= nxt[1] < ROWS:
                if grid[nxt[1]][nxt[0]] == 1: continue
                new_cost = cost[current] + 1
                if nxt not in cost or new_cost < cost[nxt]:
                    cost[nxt] = new_cost
                    heapq.heappush(pq, (new_cost + heuristic(goal, nxt), nxt))
                    came_from[nxt] = current

    path = []
    cur = goal
    while cur != start and cur in came_from:
        path.append(cur)
        cur = came_from[cur]
    path.reverse()
    return path

# ----------- Enemy Vision -----------
def can_see(player, enemy):
    x1, y1 = enemy["pos"]
    x2, y2 = player
    steps = 20
    for i in range(steps):
        t = i/steps
        x = int(x1 + (x2 - x1)*t)
        y = int(y1 + (y2 - y1)*t)
        if grid[y][x] == 1: return False
    return True

# ----------- Game Loop -----------
running = True
frame_count = 0
ENEMY_SPEED = 12  # slower enemy updates

while running:
    clock.tick(60)  # 60 FPS
    frame_count += 1

    # ----- Events -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ----- Continuous Player Movement -----
    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_LEFT]:  dx = -player_speed
    if keys[pygame.K_RIGHT]: dx = player_speed
    if keys[pygame.K_UP]:    dy = -player_speed
    if keys[pygame.K_DOWN]:  dy = player_speed

    # Attempt move
    new_x = player_pos[0] + dx
    new_y = player_pos[1] + dy
    if 0 <= int(new_x) < COLS and grid[int(player_pos[1])][int(new_x)] == 0:
        player_pos[0] = new_x
    if 0 <= int(new_y) < ROWS and grid[int(new_y)][int(player_pos[0])] == 0:
        player_pos[1] = new_y

    player_tile = [int(player_pos[0]), int(player_pos[1])]

    # ----- Enemy AI (slower) -----
    if frame_count % ENEMY_SPEED == 0:
        for e in enemies:
            if e["stun_timer"] > 0:
                e["stun_timer"] -= 1
                continue

            if can_see(player_tile, e):
                e["path"] = astar(tuple(e["pos"]), tuple(player_tile))
            else:
                if len(e["path"]) < 2:
                    target = (random.randint(1,COLS-2), random.randint(1,ROWS-2))
                    e["path"] = astar(tuple(e["pos"]), target)

            if e["path"]:
                nx, ny = e["path"].pop(0)
                e["fpos"][0] = nx
                e["fpos"][1] = ny
                e["pos"] = [nx, ny]

            if e["pos"] == player_tile:
                print("💀 GAME OVER – Enemy caught you!")
                running = False

    # ----- Treasure -----
    if player_tile == treasure:
        treasure_collected = True

    # ----- Draw -----
    win.fill(BLACK)

    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c]==1:
                pygame.draw.rect(win, GRAY, (c*TILE, r*TILE, TILE, TILE))

    # Player
    pygame.draw.rect(win, BLUE, (player_pos[0]*TILE, player_pos[1]*TILE, TILE, TILE))

    # Treasure
    if not treasure_collected:
        pygame.draw.rect(win, YELLOW, (treasure[0]*TILE, treasure[1]*TILE, TILE, TILE))

    # Enemies
    for e in enemies:
        color = RED if e["stun_timer"]==0 else CYAN
        pygame.draw.rect(win, color, (e["fpos"][0]*TILE, e["fpos"][1]*TILE, TILE, TILE))

    pygame.display.update()

    # ----- Level Complete -----
    if treasure_collected:
        print("🎉 LEVEL COMPLETE!")
        pygame.time.delay(1000)
        grid = generate_map()
        player_tile = [2,2]
        player_pos = [2.0, 2.0]
        treasure = place_treasure()
        treasure_collected = False
        enemies = [create_enemy() for _ in range(5)]
        frame_count = 0

pygame.quit()
