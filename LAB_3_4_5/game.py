# DFS Maze Game with Hint Button & Multiple Difficulty Levels
# -----------------------------------------------------------
# Controls:
#   Arrow keys  – Move
#   H or mouse  – Toggle shortest-path hint
#   1 / 2 / 3   – Easy / Medium / Hard maze size
#   R           – Restart current level
#   Esc         – Quit
# -----------------------------------------------------------
# Requires: pygame  (pip install pygame)

import pygame
import random
import sys
from collections import deque

# --------------------------- CONFIGURATION --------------------------- #
CELL_SIZE  = 24                        # pixel size of one cell
LEVELS     = {"1": (15, 15),           # Easy
              "2": (25, 25),           # Medium (default)
              "3": (35, 35)}           # Hard
FPS        = 60
WALL_COLOR   = (40, 40, 40)
HINT_COLOR   = (235, 200, 85)
PLAYER_COLOR = (0, 120, 215)
EXIT_COLOR   = (220, 50, 50)
BG_COLOR     = (15, 15, 15)
TEXT_COLOR   = (240, 240, 240)
BTN_COLOR    = (70, 70, 70)
BTN_HOVER    = (100, 100, 100)

# --------------------------- MAZE GENERATION (DFS) --------------------------- #
def generate_maze(cols, rows):
    visited = [[False]*rows for _ in range(cols)]
    walls   = [[[True]*4 for _ in range(rows)] for _ in range(cols)]  # N,E,S,W

    def valid(x, y): return 0 <= x < cols and 0 <= y < rows

    def carve(x, y):
        visited[x][y] = True
        dirs = [(0,-1,0), (1,0,1), (0,1,2), (-1,0,3)]  # dx,dy,wall-index
        random.shuffle(dirs)
        for dx, dy, w in dirs:
            nx, ny = x+dx, y+dy
            if valid(nx, ny) and not visited[nx][ny]:
                walls[x][y][w] = False
                walls[nx][ny][(w+2)%4] = False
                carve(nx, ny)
    carve(0, 0)
    return walls

# --------------------------- SHORTEST PATH (BFS) --------------------------- #
def bfs_path(walls, cols, rows, start, goal):
    q = deque([start])
    parent = {start: None}
    deltas = [(0,-1,0), (1,0,1), (0,1,2), (-1,0,3)]
    while q:
        x, y = q.popleft()
        if (x, y) == goal:
            break
        for dx, dy, w in deltas:
            nx, ny = x+dx, y+dy
            if not (0 <= nx < cols and 0 <= ny < rows): continue
            if walls[x][y][w]: continue           # wall blocks
            if (nx, ny) not in parent:
                parent[(nx, ny)] = (x, y)
                q.append((nx, ny))
    path, cur = [], goal
    while cur is not None:
        path.append(cur)
        cur = parent.get(cur)
    return list(reversed(path))            # start→goal inclusive

# --------------------------- GAME CLASS --------------------------- #
class MazeGame:
    def __init__(self, lvl="2"):
        pygame.init()
        self.font  = pygame.font.SysFont(None, 32)
        self.font2 = pygame.font.SysFont(None, 42)
        self.clock = pygame.time.Clock()
        self.set_level(lvl)

    # ----- level management -----
    def set_level(self, key):
        self.lvl_key = key
        self.cols, self.rows = LEVELS[key]
        size = (self.cols*CELL_SIZE, self.rows*CELL_SIZE + 50)  # +UI bar
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption(f"DFS Maze – Level {key}")
        self.reset()

    def reset(self):
        self.walls = generate_maze(self.cols, self.rows)
        self.pos   = [0, 0]
        self.won   = False
        self.show_hint = False
        self.hint_path = []

    # ----- drawing helpers -----
    def draw_maze(self):
        off_y = 50
        for x in range(self.cols):
            for y in range(self.rows):
                cx, cy = x*CELL_SIZE, off_y + y*CELL_SIZE
                if self.walls[x][y][0]:
                    pygame.draw.line(self.screen, WALL_COLOR, (cx, cy), (cx+CELL_SIZE, cy), 2)
                if self.walls[x][y][1]:
                    pygame.draw.line(self.screen, WALL_COLOR, (cx+CELL_SIZE, cy), (cx+CELL_SIZE, cy+CELL_SIZE), 2)
                if self.walls[x][y][2]:
                    pygame.draw.line(self.screen, WALL_COLOR, (cx, cy+CELL_SIZE), (cx+CELL_SIZE, cy+CELL_SIZE), 2)
                if self.walls[x][y][3]:
                    pygame.draw.line(self.screen, WALL_COLOR, (cx, cy), (cx, cy+CELL_SIZE), 2)

        # exit cell
        ex = pygame.Rect((self.cols-1)*CELL_SIZE+2,
                         off_y + (self.rows-1)*CELL_SIZE+2,
                         CELL_SIZE-3, CELL_SIZE-3)
        pygame.draw.rect(self.screen, EXIT_COLOR, ex)

        # hint path
        if self.show_hint:
            for (x, y) in self.hint_path:
                r = pygame.Rect(x*CELL_SIZE+8, off_y + y*CELL_SIZE+8,
                                CELL_SIZE-15, CELL_SIZE-15)
                pygame.draw.rect(self.screen, HINT_COLOR, r)

    def draw_player(self):
        off_y = 50
        x, y = self.pos
        r = pygame.Rect(x*CELL_SIZE+4, off_y + y*CELL_SIZE+4,
                        CELL_SIZE-7, CELL_SIZE-7)
        pygame.draw.rect(self.screen, PLAYER_COLOR, r)

    def draw_ui(self):
        # top bar
        pygame.draw.rect(self.screen, (25,25,25),
                         pygame.Rect(0, 0, self.screen.get_width(), 50))

        # hint button
        txt = "Show Path" if not self.show_hint else "Hide Path"
        ts  = self.font.render(txt, True, TEXT_COLOR)
        pad = 10
        btn = pygame.Rect(20, 10, ts.get_width()+pad*2, ts.get_height()+pad*2)
        hover = btn.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.screen, BTN_HOVER if hover else BTN_COLOR,
                         btn, border_radius=6)
        self.screen.blit(ts, (btn.x+pad, btn.y+pad))
        self.btn_hint = btn

        # level info
        lbl = self.font.render("Level: "+self.lvl_key+"  (1/2/3)",
                               True, TEXT_COLOR)
        self.screen.blit(lbl,
                         (self.screen.get_width()-lbl.get_width()-20, 14))

    def draw_victory(self):
        m = self.font2.render("You escaped! Press R to replay.",
                              True, TEXT_COLOR)
        rect = m.get_rect(center=(self.screen.get_width()//2,
                                  self.screen.get_height()//2))
        self.screen.blit(m, rect)

    # ----- movement & hint -----
    def move(self, dx, dy):
        if self.won: return
        dir_map = {(0,-1):0,(1,0):1,(0,1):2,(-1,0):3}
        x,y = self.pos; nx, ny = x+dx, y+dy
        if not (0<=nx<self.cols and 0<=ny<self.rows): return
        if not self.walls[x][y][dir_map[(dx,dy)]]:
            self.pos = [nx, ny]
            if self.show_hint:
                self.calc_hint()
        if self.pos == [self.cols-1, self.rows-1]:
            self.won, self.show_hint = True, False

    def calc_hint(self):
        self.hint_path = bfs_path(self.walls, self.cols, self.rows,
                                  tuple(self.pos),
                                  (self.cols-1, self.rows-1))[1:-1]

    def toggle_hint(self):
        if self.won: return
        self.show_hint = not self.show_hint
        if self.show_hint:
            self.calc_hint()

    # ----- event loop -----
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if e.key == pygame.K_r: self.reset()
                if e.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    self.set_level(chr(e.key))
                if e.key == pygame.K_h: self.toggle_hint()
                if not self.won:
                    if e.key == pygame.K_UP:    self.move(0,-1)
                    if e.key == pygame.K_DOWN:  self.move(0,1)
                    if e.key == pygame.K_LEFT:  self.move(-1,0)
                    if e.key == pygame.K_RIGHT: self.move(1,0)
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.btn_hint.collidepoint(e.pos):
                    self.toggle_hint()

    # ----- main loop -----
    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            self.screen.fill(BG_COLOR)
            self.draw_maze()
            self.draw_player()
            self.draw_ui()
            if self.won:
                self.draw_victory()
            pygame.display.flip()

# --------------------------- ENTRY POINT --------------------------- #
if __name__ == "__main__":
    MazeGame().run()
