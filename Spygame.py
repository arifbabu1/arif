import pygame  # Pygame library for graphics and game functions
import random  # Random library to generate random positions for enemies and treasure
import math    # Math library for calculations like sine for glowing effects
import heapq   # Heap queue for implementing A* pathfinding

pygame.init()  # Initialize all Pygame modules

# -------- Window Setup --------
WIDTH, HEIGHT = 1000, 800           # Screen width and height in pixels
TILE = 50                            # Size of one tile
ROWS, COLS = HEIGHT // TILE, WIDTH // TILE  # Calculate rows and columns based on TILE size
win = pygame.display.set_mode((WIDTH, HEIGHT))  # Create game window
pygame.display.set_caption("Spy Game – Realistic Player + Glowing Enemies + Book Treasure")  # Set window title

clock = pygame.time.Clock()  # Clock to control FPS

# -------- Colors --------
BLACK = (0, 0, 0)             # Background color
GRAY = (60, 60, 60)           # Wall color
SKIN = (255, 220, 180)        # Player skin color
SHIRT = (50, 100, 255)        # Player shirt color
PANTS = (40, 40, 80)          # Player pants color
SHOES = (20, 20, 20)          # Player shoes color
ENEMY_COLOR = (255, 0, 0)     # Enemy color (red)
TREASURE_COLOR = (51, 255, 255)  # Book treasure main color (electric blue)
TREASURE_GLOW = (255, 255, 255)  # Book treasure glow color (white)

# -------- Map Generation --------
def generate_map():
    """Generates a random grid map with walls (1) and empty spaces (0)"""
    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]  # Initialize empty grid
    for r in range(ROWS):
        for c in range(COLS):
            if random.random() < 0.13:  # 13% chance of placing a wall
                grid[r][c] = 1
    # Ensure starting area is empty (top-left 5x5)
    for rr in range(5):
        for cc in range(5):
            grid[rr][cc] = 0
    return grid

grid = generate_map()  # Create initial map

# -------- Player Setup --------
player_pos = [2.0, 2.0]  # Player starting position (x, y in tile units)
player_speed = 0.09      # Player movement speed per frame
PLAYER_SIZE = TILE * 0.8  # Player collision box size

# -------- Draw Realistic Player --------
def draw_player(x, y):
    """Draws a realistic human player at given tile coordinates"""
    px = int(x * TILE)  # Convert tile x to pixel x
    py = int(y * TILE)  # Convert tile y to pixel y

    # Head
    pygame.draw.circle(win, SKIN, (px + TILE//2, py + TILE//5), TILE//6)
    # Neck
    pygame.draw.rect(win, SKIN, (px + TILE//2 - 5, py + TILE//5 + 8, 10, 10))
    # Body (Shirt)
    pygame.draw.rect(win, SHIRT, (px + TILE//3, py + TILE//3, TILE//3, TILE//2))
    # Left Arm
    pygame.draw.rect(win, SKIN, (px + TILE//3 - 10, py + TILE//3, 10, TILE//3))
    # Right Arm
    pygame.draw.rect(win, SKIN, (px + TILE//3 + TILE//3, py + TILE//3, 10, TILE//3))
    # Pants
    pygame.draw.rect(win, PANTS, (px + TILE//3, py + TILE//3 + TILE//2, TILE//3, TILE//4))
    # Shoes
    pygame.draw.rect(win, SHOES, (px + TILE//3, py + TILE//3 + TILE//2 + TILE//4, TILE//6, TILE//6))
    pygame.draw.rect(win, SHOES, (px + TILE//2, py + TILE//3 + TILE//2 + TILE//4, TILE//6, TILE//6))

# -------- Treasure Drawing (Book) --------
def draw_book_treasure(tx, ty, frame):
    """Draws a glowing book-shaped treasure at tile coordinates"""
    cx = tx * TILE + TILE // 2  # Pixel center x
    cy = ty * TILE + TILE // 2  # Pixel center y

    # Glowing effect using sine for pulsation
    glow_size = int(5 + 3 * math.sin(frame * 0.15))
    glow_rect = pygame.Rect(cx - TILE//4 - glow_size, cy - TILE//5 - glow_size,
                            TILE//2 + 2*glow_size, TILE//2 + 2*glow_size)
    pygame.draw.rect(win, TREASURE_GLOW, glow_rect)  # Draw glow

    # Book shape rectangle
    book_rect = pygame.Rect(cx - TILE//4, cy - TILE//5, TILE//2, TILE//2)
    pygame.draw.rect(win, TREASURE_COLOR, book_rect)
    # Book spine
    pygame.draw.line(win, BLACK, (cx - TILE//4, cy - TILE//5),
                     (cx - TILE//4, cy + TILE//5 + TILE//10), 2)

# -------- Enemy Drawing (Glowing Red) --------
def draw_enemy(x, y, frame):
    """Draws a glowing enemy at tile coordinates"""
    cx = int(x * TILE + TILE/2)
    cy = int(y * TILE + TILE/2)

    glow_size = int(5 + 3 * math.sin(frame * 0.2))
    pygame.draw.circle(win, (255, 100, 100), (cx, cy), TILE//2 - 5 + glow_size)  # Glow effect
    pygame.draw.circle(win, ENEMY_COLOR, (cx, cy), TILE//2 - 5)  # Main enemy circle

# -------- Treasure Placement --------
def place_treasure():
    """Randomly places treasure on empty grid tiles"""
    while True:
        r = random.randint(1, ROWS-2)
        c = random.randint(1, COLS-2)
        if grid[r][c] == 0:
            return [c, r]

treasure = place_treasure()
treasure_collected = False

# -------- Enemy AI --------
def create_enemy():
    """Randomly create an enemy on empty grid tile"""
    while True:
        r = random.randint(0, ROWS-1)
        c = random.randint(0, COLS-1)
        if grid[r][c] == 0:
            return {"pos": [c, r], "path": []}

def heuristic(a, b):
    """Manhattan distance for A*"""
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar(start, goal):
    """A* pathfinding from start to goal on grid"""
    neighbors = [(1,0),(-1,0),(0,1),(0,-1)]
    pq = []
    heapq.heappush(pq, (0, start))
    came = {}
    cost = {start: 0}

    while pq:
        _, curr = heapq.heappop(pq)
        if curr == goal: break
        for dx, dy in neighbors:
            nxt = (curr[0]+dx, curr[1]+dy)
            if 0 <= nxt[0] < COLS and 0 <= nxt[1] < ROWS:
                if grid[nxt[1]][nxt[0]] == 1: continue
                new_cost = cost[curr] + 1
                if nxt not in cost or new_cost < cost[nxt]:
                    cost[nxt] = new_cost
                    heapq.heappush(pq, (new_cost + heuristic(goal, nxt), nxt))
                    came[nxt] = curr

    path = []
    cur = goal
    while cur != start and cur in came:
        path.append(cur)
        cur = came[cur]
    path.reverse()
    return path

def can_see(px, py, ex, ey):
    """Enemy can see player if within Manhattan distance <10"""
    return abs(px-ex) + abs(py-ey) < 10

enemies = [create_enemy() for _ in range(5)]  # Initialize 5 enemies

# -------- Main Game Loop --------
running = True
frame = 0
ENEMY_RATE = 40  # How often enemies recalc path

while running:
    clock.tick(60)  # Limit to 60 FPS
    frame += 1

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False  # Exit game if window closed

    # -------- Player Movement with boundaries --------
    keys = pygame.key.get_pressed()
    dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player_speed
    dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * player_speed

    new_x = max(0, min(COLS - 1, player_pos[0] + dx))
    new_y = max(0, min(ROWS - 1, player_pos[1] + dy))

    # Collision with walls
    if grid[int(player_pos[1])][int(new_x)] == 0:
        player_pos[0] = new_x
    if grid[int(new_y)][int(player_pos[0])] == 0:
        player_pos[1] = new_y

    p_tile = [int(player_pos[0]), int(player_pos[1])]

    # -------- Enemy AI movement --------
    if frame % ENEMY_RATE == 0:
        for e in enemies:
            ex, ey = e["pos"]

            if can_see(p_tile[0], p_tile[1], ex, ey):
                e["path"] = astar((ex, ey), (p_tile[0], p_tile[1]))  # Chase player
            else:
                if len(e["path"]) < 1:
                    target = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
                    e["path"] = astar((ex, ey), target)  # Random movement

            if e["path"]:
                nx, ny = e["path"].pop(0)
                e["pos"] = [nx, ny]

            if e["pos"] == p_tile:
                print("💀 Enemy caught you!")
                running = False

    # -------- Treasure Collection Check --------
    if p_tile == treasure:
        treasure_collected = True

    # -------- Drawing --------
    win.fill(BLACK)  # Clear screen

    # Draw walls
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] == 1:
                pygame.draw.rect(win, GRAY, (c*TILE, r*TILE, TILE, TILE))

    # Draw player
    draw_player(player_pos[0], player_pos[1])

    # Draw treasure
    if not treasure_collected:
        draw_book_treasure(treasure[0], treasure[1], frame)

    # Draw enemies
    for e in enemies:
        draw_enemy(e["pos"][0], e["pos"][1], frame)

    pygame.display.update()  # Update display

    # -------- Next Level Reset --------
    if treasure_collected:
        print("🎉 Level Complete!")
        pygame.time.delay(700)
        grid = generate_map()
        treasure = place_treasure()
        treasure_collected = False
        player_pos = [2.0, 2.0]
        enemies = [create_enemy() for _ in range(5)]

pygame.quit()  # Quit Pygame when loop ends
