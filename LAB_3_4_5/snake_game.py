import pygame
import random
import collections

# --- Game Configuration ---
GRID_SIZE = 20  # Number of cells in width and height
CELL_SIZE = 30  # Size of each cell in pixels
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE + 60  # Extra space for score and status

# Colors
COLOR_BACKGROUND = (40, 40, 40)  # Dark Gray
COLOR_GRID = (60, 60, 60)  # Lighter Gray for grid lines
COLOR_SNAKE = (0, 255, 127)  # Spring Green
COLOR_SNAKE_HEAD = (0, 200, 100)  # Darker Green for head
COLOR_FOOD = (255, 69, 0)  # OrangeRed
COLOR_OBSTACLE = (138, 43, 226)  # BlueViolet
COLOR_TEXT = (255, 255, 255)  # White
COLOR_SCORE_TEXT = (255, 215, 0)  # Gold
COLOR_GAME_OVER_BG = (0, 0, 0, 180)  # Semi-transparent black
COLOR_AUTOPILOT_ON = (0, 255, 0)  # Green
COLOR_AUTOPILOT_OFF = (255, 0, 0)  # Red

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


# --- Helper Functions ---
def draw_grid(surface):
    """Draws the grid lines on the game surface."""
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT - 60))
    for y in range(0, SCREEN_HEIGHT - 60, CELL_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (0, y), (SCREEN_WIDTH, y))


def get_random_position(snake_body, obstacles, food_pos=None):
    """Gets a random position on the grid not occupied by snake, obstacles, or existing food."""
    while True:
        pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        if pos not in snake_body and pos not in obstacles and (food_pos is None or pos != food_pos):
            return pos


# --- Snake Class ---
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        """Resets the snake to its initial state."""
        self.length = 1
        # Start in the middle of the grid
        self.positions = [((GRID_SIZE // 2), (GRID_SIZE // 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = COLOR_SNAKE
        self.head_color = COLOR_SNAKE_HEAD
        self.score = 0

    def get_head_position(self):
        """Returns the position of the snake's head."""
        return self.positions[0]

    def turn(self, point):
        """Changes the snake's direction, preventing 180-degree turns."""
        if self.length > 1 and (point[0] * -1, point[1] * -1) == self.direction:
            return  # Prevent turning back on itself
        else:
            self.direction = point

    def move(self):
        """Moves the snake in its current direction."""
        cur = self.get_head_position()
        x, y = self.direction
        new_head = (((cur[0] + x) % GRID_SIZE), ((cur[1] + y) % GRID_SIZE))  # Wrap around screen

        # Check for collision with self
        if len(self.positions) > 2 and new_head in self.positions[2:]:
            return True  # Collision occurred

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()
        return False  # No collision

    def grow(self):
        """Increases the length of the snake and score."""
        self.length += 1
        self.score += 1

    def draw(self, surface):
        """Draws the snake on the game surface."""
        for i, p in enumerate(self.positions):
            r = pygame.Rect((p[0] * CELL_SIZE, p[1] * CELL_SIZE), (CELL_SIZE, CELL_SIZE))
            if i == 0:  # Head
                pygame.draw.rect(surface, self.head_color, r)
                pygame.draw.rect(surface, COLOR_SNAKE, r, 3)  # Border for head
            else:  # Body
                pygame.draw.rect(surface, self.color, r)
                pygame.draw.rect(surface, self.head_color, r, 1)  # Thinner border for body


# --- Food Class ---
class Food:
    def __init__(self, snake_body, obstacles):
        self.color = COLOR_FOOD
        self.position = get_random_position(snake_body, obstacles)

    def randomize_position(self, snake_body, obstacles):
        """Places the food at a new random position."""
        self.position = get_random_position(snake_body, obstacles, self.position)

    def draw(self, surface):
        """Draws the food on the game surface."""
        r = pygame.Rect((self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE), (CELL_SIZE, CELL_SIZE))
        pygame.draw.ellipse(surface, self.color, r)  # Draw as a circle/ellipse


# --- Obstacle Class ---
class Obstacles:
    def __init__(self, num_obstacles, snake_body):
        self.color = COLOR_OBSTACLE
        self.positions = []
        self.num_obstacles = num_obstacles
        self.generate_obstacles(snake_body)

    def generate_obstacles(self, snake_body):
        """Generates a set of obstacles."""
        self.positions = []
        # Ensure obstacles are not too close to the initial snake position
        safe_spawn_area_for_snake = set()
        head = snake_body[0]
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                safe_spawn_area_for_snake.add((head[0] + dx, head[1] + dy))

        for _ in range(self.num_obstacles):
            pos = get_random_position(snake_body + list(safe_spawn_area_for_snake), self.positions)
            self.positions.append(pos)

    def draw(self, surface):
        """Draws the obstacles on the game surface."""
        for p in self.positions:
            r = pygame.Rect((p[0] * CELL_SIZE, p[1] * CELL_SIZE), (CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(surface, self.color, r)
            pygame.draw.rect(surface, COLOR_BACKGROUND, r, 2)  # Border


# --- BFS Autopilot ---
def bfs_pathfinding(start_pos, target_pos, snake_body, obstacles):
    """
    Finds the shortest path from start_pos to target_pos using BFS.
    Avoids snake_body and obstacles.
    Returns a list of positions representing the path, or an empty list if no path found.
    """
    queue = collections.deque([[start_pos]])
    visited = {start_pos}

    # The grid for BFS considers the snake's body (except its current head, which will move)
    # and obstacles as blocked.
    # When considering next moves, the snake's *future* head position is what matters.
    # The current snake body (excluding the tail if it moves) becomes an obstacle for the *next* step.

    while queue:
        path = queue.popleft()
        current_head = path[-1]

        if current_head == target_pos:
            return path[1:]  # Return path excluding the current head itself

        for dx, dy in [UP, DOWN, LEFT, RIGHT]:
            next_x, next_y = current_head[0] + dx, current_head[1] + dy

            # Check boundaries (though snake wraps, BFS might be better with fixed boundaries for pathing)
            if not (0 <= next_x < GRID_SIZE and 0 <= next_y < GRID_SIZE):
                continue

            next_pos = (next_x, next_y)

            # Check collision with obstacles or snake's body
            # For BFS, the snake's body (except its tail, which will move away) is an obstacle.
            # The critical part is that the *entire* snake body (as it would be *after* the move)
            # should not collide with the `next_pos`.
            # A simpler BFS: treat all current snake segments (except perhaps the tail if it's about to move) as obstacles.
            if next_pos in visited or next_pos in obstacles or next_pos in snake_body[
                                                                           :-1]:  # snake_body[:-1] to allow moving into tail's old spot
                continue

            new_path = list(path)
            new_path.append(next_pos)
            queue.append(new_path)
            visited.add(next_pos)

    return []  # No path found


# --- Main Game ---
def game_loop():
    pygame.init()
    pygame.font.init()  # Initialize font module

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    pygame.display.set_caption("Fantastic Snake Game")
    surface = pygame.Surface(screen.get_size())
    surface = surface.convert()  # For performance

    font_path = None  # Let Pygame find a default system font if "PressStart2P" is not available
    try:
        # Attempt to use a specific retro font if available (e.g., place PressStart2P-Regular.ttf in same dir)
        # pygame.font.get_fonts() can show available system fonts
        if "pressstart2p" in pygame.font.get_fonts():
            font_path = "pressstart2p"

        # If not found, try to load from a local file (common practice)
        if not font_path:
            # Check if font file exists locally
            local_font_path = "PressStart2P-Regular.ttf"  # Common name for the font file
            if pygame.font.match_font(local_font_path):  # Check if Pygame can find it
                font_path = local_font_path

    except Exception as e:
        print(f"Font loading error: {e}. Using default system font.")
        font_path = None

    try:
        score_font = pygame.font.Font(font_path, 24)  # Larger for score
        status_font = pygame.font.Font(font_path, 18)  # Smaller for status
        game_over_font_big = pygame.font.Font(font_path, 48)
        game_over_font_small = pygame.font.Font(font_path, 20)
    except pygame.error:  # Fallback if font is still not found
        print("Specific font not found, using Pygame default font.")
        score_font = pygame.font.SysFont(None, 36)
        status_font = pygame.font.SysFont(None, 28)
        game_over_font_big = pygame.font.SysFont(None, 72)
        game_over_font_small = pygame.font.SysFont(None, 30)

    clock = pygame.time.Clock()

    snake = Snake()
    num_initial_obstacles = 5  # Adjust as needed
    obstacles = Obstacles(num_initial_obstacles, snake.positions)
    food = Food(snake.positions, obstacles.positions)

    game_over = False
    autopilot_on = False
    autopilot_path = []

    # --- Initial Game State Setup ---
    def reset_game_state():
        nonlocal snake, obstacles, food, game_over, autopilot_path, autopilot_on
        snake.reset()
        obstacles.generate_obstacles(snake.positions)  # Regenerate obstacles away from new snake
        food.randomize_position(snake.positions, obstacles.positions)
        game_over = False
        autopilot_path = []
        # autopilot_on = False # Optionally reset autopilot state too

    reset_game_state()  # Initial setup

    # --- Game Loop ---
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return  # Exit the game loop and function
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        reset_game_state()
                else:
                    if not autopilot_on:  # Manual controls only if autopilot is off
                        if event.key == pygame.K_UP:
                            snake.turn(UP)
                        elif event.key == pygame.K_DOWN:
                            snake.turn(DOWN)
                        elif event.key == pygame.K_LEFT:
                            snake.turn(LEFT)
                        elif event.key == pygame.K_RIGHT:
                            snake.turn(RIGHT)
                    if event.key == pygame.K_a:  # Toggle Autopilot
                        autopilot_on = not autopilot_on
                        autopilot_path = []  # Clear path on toggle
                    if event.key == pygame.K_ESCAPE:  # Quit game
                        pygame.quit()
                        return

        if not game_over:
            collision_with_self = False
            if autopilot_on:
                if not autopilot_path:  # If no path or path completed, find new one
                    # Important: For BFS, the snake's body to avoid is all current segments
                    # *except* the tail, because the tail will move out of the way.
                    # If the snake is very short (length 1 or 2), this needs care.
                    body_to_avoid_for_bfs = snake.positions
                    if snake.length > 1:
                        body_to_avoid_for_bfs = snake.positions[:-1]

                    path_to_food = bfs_pathfinding(snake.get_head_position(), food.position, body_to_avoid_for_bfs,
                                                   obstacles.positions)

                    if path_to_food:
                        autopilot_path = path_to_food
                    else:
                        # No path to food, try to make a "safe" move (survival instinct)
                        # Find any adjacent valid square not hitting self or obstacle
                        head = snake.get_head_position()
                        possible_moves = []
                        for dx_safe, dy_safe in [UP, DOWN, LEFT, RIGHT]:
                            next_safe_pos = ((head[0] + dx_safe) % GRID_SIZE, (head[1] + dy_safe) % GRID_SIZE)
                            if next_safe_pos not in snake.positions and next_safe_pos not in obstacles.positions:
                                # Optional: Prefer moves that don't immediately reverse current direction unless necessary
                                if snake.length > 1 and (dx_safe, dy_safe) == (
                                snake.direction[0] * -1, snake.direction[1] * -1):
                                    if len(possible_moves) > 1:  # Only consider reverse if it's not the only option or only few options
                                        continue
                                possible_moves.append((dx_safe, dy_safe))

                        if possible_moves:
                            # Simple: pick a random safe move, or prioritize current direction if safe
                            if snake.direction in possible_moves:
                                snake.turn(snake.direction)
                            else:
                                snake.turn(random.choice(possible_moves))
                            autopilot_path = []  # No specific path, just one safe step
                        else:
                            # Truly stuck, will likely lead to game over in next move if no safe spot
                            autopilot_path = []

                if autopilot_path:  # If there's a path to follow
                    next_move_pos = autopilot_path.pop(0)
                    head_pos = snake.get_head_position()
                    dx = next_move_pos[0] - head_pos[0]
                    dy = next_move_pos[1] - head_pos[1]

                    # Handle wrap-around for dx, dy calculation if next_move_pos is across the screen edge
                    if dx > 1:
                        dx = -1
                    elif dx < -1:
                        dx = 1
                    if dy > 1:
                        dy = -1
                    elif dy < -1:
                        dy = 1

                    snake.turn((dx, dy))

            collision_with_self = snake.move()  # Move snake and check self-collision

            # Check collision with obstacles
            if snake.get_head_position() in obstacles.positions:
                game_over = True

            # Check collision with self (again, move might have caused it)
            if collision_with_self:  # snake.move() now returns True on self-collision
                game_over = True

            # Check if snake ate food
            if snake.get_head_position() == food.position:
                snake.grow()
                food.randomize_position(snake.positions, obstacles.positions)
                autopilot_path = []  # Recalculate path after eating

        # --- Drawing ---
        surface.fill(COLOR_BACKGROUND)
        draw_grid(surface)  # Draw grid lines underneath other elements

        snake.draw(surface)
        food.draw(surface)
        obstacles.draw(surface)

        # Draw Score
        score_text_surf = score_font.render(f"SCORE: {snake.score}", True, COLOR_SCORE_TEXT)
        score_rect = score_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 45))
        surface.blit(score_text_surf, score_rect)

        # Draw Autopilot Status
        autopilot_status_text = "AUTOPILOT: ON" if autopilot_on else "AUTOPILOT: OFF"
        autopilot_status_color = COLOR_AUTOPILOT_ON if autopilot_on else COLOR_AUTOPILOT_OFF
        autopilot_surf = status_font.render(autopilot_status_text, True, autopilot_status_color)
        autopilot_rect = autopilot_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 18))
        surface.blit(autopilot_surf, autopilot_rect)

        if game_over:
            # Create a semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - 60), pygame.SRCALPHA)
            overlay.fill(COLOR_GAME_OVER_BG)
            surface.blit(overlay, (0, 0))

            game_over_text_big = game_over_font_big.render("GAME OVER", True, COLOR_TEXT)
            text_rect_big = game_over_text_big.get_rect(center=(SCREEN_WIDTH // 2, (SCREEN_HEIGHT - 60) // 2 - 30))
            surface.blit(game_over_text_big, text_rect_big)

            final_score_text = game_over_font_small.render(f"Final Score: {snake.score}", True, COLOR_SCORE_TEXT)
            final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, (SCREEN_HEIGHT - 60) // 2 + 20))
            surface.blit(final_score_text, final_score_rect)

            restart_text = game_over_font_small.render("Press 'R' to Restart", True, COLOR_TEXT)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, (SCREEN_HEIGHT - 60) // 2 + 60))
            surface.blit(restart_text, restart_rect)

        screen.blit(surface, (0, 0))
        pygame.display.flip()  # Use flip for full screen update
        pygame.display.update()  # Or update specific rects if optimizing later

        # Control game speed
        # Speed can be increased based on score for progressive difficulty
        game_speed = 10 + (snake.score // 5)  # Increase speed every 5 points
        clock.tick(min(game_speed, 30))  # Cap speed at 30 FPS


if __name__ == '__main__':
    game_loop()