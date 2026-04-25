import pygame
import copy
import random

SHAPES = {
    'I': [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
    'J': [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
    'L': [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
    'O': [[1, 1], [1, 1]], 
    'S': [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
    'T': [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
    'Z': [[1, 1, 0], [0, 1, 1], [0, 0, 0]]
}

COLORS = {
    'I': (0, 255, 255), 'J': (0, 0, 255), 'L': (255, 165, 0),
    'O': (255, 255, 0), 'S': (0, 255, 0), 'T': (128, 0, 128), 'Z': (255, 0, 0)
}

CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20

class Block():
    def __init__(self, shapes):
        self.name = shapes 
        self.matrix = copy.deepcopy(SHAPES[shapes])
        self.color = COLORS[shapes] 
        self.x = 3  
        self.y = 0  

    def rotate(self):
        n = len(self.matrix)
        for i in range(n):
            for j in range(i, n):
                self.matrix[i][j], self.matrix[j][i] = self.matrix[j][i], self.matrix[i][j]
        for i in range(n):
            self.matrix[i].reverse()

    def rotate_back(self):
        for _ in range(3):
            self.rotate()

class TetrisBoard():
    def __init__(self, screen, offset_x, title, controls):
        self.screen = screen
        self.offset_x = offset_x
        self.title = title
        self.controls = controls
        
        self.font = pygame.font.SysFont('Consolas', 24, bold=True)
        self.game_over_font = pygame.font.SysFont('Consolas', 50, bold=True)
        
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.game_over = False

        self.next_queue = []
        self.fill_queue() 
        self.current_piece = self.next_queue.pop(0)
        self.held_piece = None
        self.can_swap = True 

        self.fall_time = 0
        self.fall_speed = 350

    def get_random_block(self):
        return Block(random.choice(list(SHAPES.keys())))

    def fill_queue(self):
        while len(self.next_queue) < 4:
            self.next_queue.append(self.get_random_block())

    def is_collision(self, nblock: Block):
        for i, row in enumerate(nblock.matrix):
            for j, cell in enumerate(row):
                if cell != 0:
                    x = nblock.x + j
                    y = nblock.y + i
                    if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT or (y >= 0 and self.grid[y][x] != 0):
                        return True
        return False

    def lock_piece(self):
        for i, row in enumerate(self.current_piece.matrix):
            for j, cell in enumerate(row):
                if cell != 0:
                    if self.current_piece.y + i >= 0:
                        self.grid[self.current_piece.y + i][self.current_piece.x + j] = self.current_piece.color

    def clear_lines(self):
        line_count = 0
        i = GRID_HEIGHT - 1
        while i >= 0:
            if 0 not in self.grid[i]:
                line_count += 1
                del self.grid[i]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            else:
                i -= 1
        if line_count > 0:
            self.score += (line_count * 100) * line_count

    def get_ghost(self):
        ghost = copy.deepcopy(self.current_piece)
        while not self.is_collision(ghost):
            ghost.y += 1
        ghost.y -= 1
        return ghost

    def spawn_next(self):
        self.fill_queue()
        self.current_piece = self.next_queue.pop(0)
        self.can_swap = True
        if self.is_collision(self.current_piece):
            self.game_over = True

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and not self.game_over:
            if event.key == self.controls['LEFT']:
                self.current_piece.x -= 1
                if self.is_collision(self.current_piece): self.current_piece.x += 1
            elif event.key == self.controls['RIGHT']:
                self.current_piece.x += 1
                if self.is_collision(self.current_piece): self.current_piece.x -= 1
            elif event.key == self.controls['DOWN']:
                self.current_piece.y += 1
                if self.is_collision(self.current_piece): self.current_piece.y -= 1
            elif event.key == self.controls['UP']:
                self.current_piece.rotate()
                if self.is_collision(self.current_piece): self.current_piece.rotate_back()
            elif event.key == self.controls['DROP']:
                ghost = self.get_ghost()
                self.current_piece.y = ghost.y
                self.lock_piece()
                self.clear_lines()
                self.spawn_next()
            elif event.key == self.controls['HOLD'] and self.can_swap:
                if self.held_piece is None:
                    self.held_piece = self.current_piece
                    self.spawn_next()
                else:
                    self.current_piece, self.held_piece = self.held_piece, self.current_piece
                    self.current_piece.x = 3
                    self.current_piece.y = 0
                    self.current_piece.matrix = copy.deepcopy(SHAPES[self.current_piece.name])
                self.can_swap = False

    def update(self, dt):
        if self.game_over: return
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.current_piece.y += 1
            if self.is_collision(self.current_piece):
                self.current_piece.y -= 1
                self.lock_piece()
                self.clear_lines()
                self.spawn_next()
            self.fall_time = 0

    def draw_piece(self, piece, start_x=0, start_y=0, is_ghost=False, scale=1.0):
        for i, row in enumerate(piece.matrix):
            for j, cell in enumerate(row):
                if cell != 0:
                    x = self.offset_x + start_x + (piece.x + j) * (CELL_SIZE * scale)
                    y = start_y + (piece.y + i) * (CELL_SIZE * scale)
                    rect = pygame.Rect(x, y, CELL_SIZE * scale, CELL_SIZE * scale)
                    if is_ghost:
                        pygame.draw.rect(self.screen, piece.color, rect, 2)
                    else:
                        pygame.draw.rect(self.screen, piece.color, rect)
                        pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)

    def draw(self):
        grid_rect = pygame.Rect(self.offset_x, 0, GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)
        pygame.draw.rect(self.screen, (50, 50, 50), grid_rect, 2)
        
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                rect = pygame.Rect(self.offset_x + c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.grid[r][c] != 0:
                    pygame.draw.rect(self.screen, self.grid[r][c], rect)
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)
                else:
                    pygame.draw.rect(self.screen, (35, 35, 35), rect, 1)

        panel_x = self.offset_x + GRID_WIDTH * CELL_SIZE + 20
        self.screen.blit(self.font.render(self.title, True, (255, 255, 0)), (panel_x, 10))
        self.screen.blit(self.font.render(f"SCORE: {self.score}", True, (0, 255, 255)), (panel_x, 45))

        pygame.draw.rect(self.screen, (30, 30, 30), (panel_x - 10, 80, 180, 250))
        self.screen.blit(self.font.render("NEXT:", True, (255, 255, 255)), (panel_x, 90))
        p_next = copy.deepcopy(self.next_queue[0])
        p_next.x, p_next.y = 0, 0
        self.draw_piece(p_next, start_x=GRID_WIDTH * CELL_SIZE + 50, start_y=130, scale=0.7)
        
        p_next_2 = copy.deepcopy(self.next_queue[1])
        p_next_2.x, p_next_2.y = 0, 0
        self.draw_piece(p_next_2, start_x=GRID_WIDTH * CELL_SIZE + 50, start_y=220, scale=0.7)

        pygame.draw.rect(self.screen, (30, 30, 30), (panel_x - 10, 350, 180, 120))
        self.screen.blit(self.font.render("HOLD:", True, (255, 255, 255)), (panel_x, 360))
        if self.held_piece:
            p_hold = copy.deepcopy(self.held_piece)
            p_hold.x, p_hold.y = 0, 0
            self.draw_piece(p_hold, start_x=GRID_WIDTH * CELL_SIZE + 50, start_y=390, scale=0.7)

        if not self.game_over:
            self.draw_piece(self.get_ghost(), is_ghost=True)
            self.draw_piece(self.current_piece)
        else:
            msg = self.game_over_font.render("GAME OVER", True, (255, 50, 50))
            m_rect = msg.get_rect(center=(self.offset_x + (GRID_WIDTH * CELL_SIZE)//2, (GRID_HEIGHT * CELL_SIZE)//2))
            self.screen.blit(msg, m_rect)

class TetrisDualApp():
    def __init__(self):
        pygame.init()
        self.board_w = GRID_WIDTH * CELL_SIZE + 200
        self.margin = 20
        self.screen = pygame.display.set_mode((self.board_w * 2 + self.margin, GRID_HEIGHT * CELL_SIZE))
        pygame.display.set_caption("Tetris Dual PvP - DSA Project")
        self.clock = pygame.time.Clock()

        p1_keys = {'LEFT': pygame.K_a, 'RIGHT': pygame.K_d, 'DOWN': pygame.K_s, 'UP': pygame.K_w, 'DROP': pygame.K_SPACE, 'HOLD': pygame.K_LSHIFT}
        p2_keys = {'LEFT': pygame.K_LEFT, 'RIGHT': pygame.K_RIGHT, 'DOWN': pygame.K_DOWN, 'UP': pygame.K_UP, 'DROP': pygame.K_RETURN, 'HOLD': pygame.K_RSHIFT}

        self.p1 = TetrisBoard(self.screen, 0, "PLAYER 1 (WASD)", p1_keys)
        self.p2 = TetrisBoard(self.screen, self.board_w + self.margin, "PLAYER 2 (Arrows)", p2_keys)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False 
                
                self.p1.handle_input(event)
                self.p2.handle_input(event)

            self.p1.update(dt)
            self.p2.update(dt)

            self.screen.fill((15, 15, 15))
            pygame.draw.line(self.screen, (80, 80, 80), (self.board_w + 10, 0), (self.board_w + 10, GRID_HEIGHT * CELL_SIZE), 2)
            self.p1.draw()
            self.p2.draw()
            pygame.display.flip()
            
        return 

if __name__ == "__main__":
    app = TetrisDualApp()
    app.run()