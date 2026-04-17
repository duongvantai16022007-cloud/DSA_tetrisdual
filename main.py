import pygame
import sys
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
class block():
    def __init__(self, shapes):
        self.name = shapes 
        self.matrix = copy.deepcopy(SHAPES[shapes]) #block
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
class game():
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('Consolas', 24, bold=True)
        window_width = GRID_WIDTH * CELL_SIZE + 200
        window_height = GRID_HEIGHT * CELL_SIZE
        self.game_over_font = pygame.font.SysFont('Consolas', 60, bold=True)

        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Tetris OOP - DSA Project")
        self.clock = pygame.time.Clock()
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        self.score = 0
        self.game_over = False
        #lưu trữ khối 
        self.next_queue = []
        self.them_vao()
        self.current_piece = self.next_queue.pop(0)
        self.held_piece = None
        self.can_swap = True
        #time
        self.fall_time = 0
        self.fall_speed = 20
    def random_block(self):
        return block(random.choice(list(SHAPES.keys())))
    def them_vao(self):
        while len(self.next_queue) < 3:
            self.next_queue.append(self.random_block())
    def is_collision(self, nblock: block):
        for i, row in enumerate(nblock.matrix):
            for j, cell in enumerate(row):
                if cell != 0:
                    x = nblock.x + j
                    y = nblock.y + i
                    if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT or (y >= 0 and self.grid[y][x] != 0):
                        return True
        return False
    def after_collision(self): #stop if return true
        for i, row in enumerate(self.current_piece.matrix):
            for j, cell in enumerate(row):
                if cell != 0:
                    if self.current_piece.y + i >= 0:
                        #đưa block vào lưới và dừng lại nếu gặp vật cản
                        self.grid[self.current_piece.y + i][self.current_piece.x + j] = self.current_piece.color
    def clear_score(self):
        line = 0
        i = GRID_HEIGHT - 1
        while i >= 0:
            if 0 not in self.grid[i]:
                line +=1
                del self.grid[i]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            else:
                i -= 1
        if line > 0:
            self.score += (line * 100) * line
    def get_ghost(self):
        ghost = copy.deepcopy(self.current_piece)
        while not self.is_collision(ghost):
            ghost.y += 1
        ghost.y -= 1
        return ghost
    def __game_over(self):
        self.them_vao()
        self.current_piece = self.next_queue.pop(0)
        self.can_swap = True
        if self.is_collision(self.current_piece):
            self.game_over = True
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and not self.game_over:
            if event.key == pygame.K_LEFT:
                self.current_piece.x -= 1
                if self.is_collision(self.current_piece): self.current_piece.x += 1
            elif event.key == pygame.K_RIGHT:
                self.current_piece.x += 1
                if self.is_collision(self.current_piece): self.current_piece.x -= 1
            elif event.key == pygame.K_DOWN:
                self.current_piece.y += 1
                if self.is_collision(self.current_piece): self.current_piece.y -= 1
            elif event.key == pygame.K_UP:
                self.current_piece.rotate()
                if self.is_collision(self.current_piece): self.current_piece.rotate_back()
            elif event.key == pygame.K_SPACE:
                ghost = self.get_ghost()
                self.current_piece.y = ghost.y
                self.after_collision()
                self.clear_score()
                self.__game_over()
            elif (event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT or event.key == pygame.K_c) and self.can_swap:
                if self.held_piece is None:
                    self.held_piece = self.current_piece
                    self.game_over()
                else:
                    self.current_piece, self.held_piece = self.held_piece, self.current_piece
                    self.current_piece.x = 3
                    self.current_piece.y = 0
                    self.current_piece.matrix = copy.deepcopy(SHAPES[self.current_piece.name])
                self.can_swap = False
    def update(self):
        if self.game_over: return #stop game
        self.fall_time += self.clock.get_rawtime()
        if self.fall_time >= self.fall_speed:
            self.current_piece.y += 1
            if self.is_collision(self.current_piece):
                self.current_piece.y -= 1
                self.after_collision()
                self.clear_score()
                self.__game_over()
            self.fall_time = 0
    def draw_piece(self, piece, start_x=0, start_y=0, is_ghost=False, scale=1.0):
        for i, row in enumerate(piece.matrix):
            for j, cell in enumerate(row):
                if cell != 0:
                    x = start_x + (piece.x + j) * (CELL_SIZE * scale)
                    y = start_y + (piece.y + i) * (CELL_SIZE * scale)
                    rect = pygame.Rect(x, y, CELL_SIZE * scale, CELL_SIZE * scale)
                    if is_ghost:
                        pygame.draw.rect(self.screen, piece.color, rect, 2)
                    else:
                        pygame.draw.rect(self.screen, piece.color, rect)
                        pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)

    def draw(self):
        self.screen.fill((20, 20, 20))
        
        # 1. Vẽ UI Text
        score_text = self.font.render(f"SCORE:", True, (255, 255, 255))
        score_val = self.font.render(f"{self.score}", True, (0, 255, 255))
        self.screen.blit(score_text, (GRID_WIDTH * CELL_SIZE + 20, 20))
        self.screen.blit(score_val, (GRID_WIDTH * CELL_SIZE + 20, 50))

        # 2. Vẽ Khung Next
        pygame.draw.rect(self.screen, (30, 30, 30), (GRID_WIDTH * CELL_SIZE + 10, 100, 180, 200))
        self.screen.blit(self.font.render("NEXT:", True, (255, 255, 255)), (GRID_WIDTH * CELL_SIZE + 20, 110))
        
        # Lợi dụng hàm draw_piece với scale nhỏ để vẽ preview
        preview_1 = copy.deepcopy(self.next_queue[0])
        preview_1.x, preview_1.y = 0, 0
        self.draw_piece(preview_1, start_x=GRID_WIDTH * CELL_SIZE + 50, start_y=150, scale=0.7)
        
        preview_2 = copy.deepcopy(self.next_queue[1])
        preview_2.x, preview_2.y = 0, 0
        self.draw_piece(preview_2, start_x=GRID_WIDTH * CELL_SIZE + 50, start_y=220, scale=0.7)

        # 3. Vẽ Khung Hold
        pygame.draw.rect(self.screen, (30, 30, 30), (GRID_WIDTH * CELL_SIZE + 10, 320, 180, 120))
        self.screen.blit(self.font.render("HOLD:", True, (255, 255, 255)), (GRID_WIDTH * CELL_SIZE + 20, 330))
        if self.held_piece:
            hold_preview = copy.deepcopy(self.held_piece)
            hold_preview.x, hold_preview.y = 0, 0
            self.draw_piece(hold_preview, start_x=GRID_WIDTH * CELL_SIZE + 50, start_y=360, scale=0.7)

        # 4. Vẽ lưới và biên
        pygame.draw.line(self.screen, (100, 100, 100), (GRID_WIDTH * CELL_SIZE, 0), (GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE), 2)
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.grid[r][c] == 0:
                    pygame.draw.rect(self.screen, (40, 40, 40), rect, 1)
                else:
                    pygame.draw.rect(self.screen, self.grid[r][c], rect)
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)

        # 5. Vẽ khối gạch
        if not self.game_over:
            ghost_piece = self.get_ghost()
            self.draw_piece(ghost_piece, is_ghost=True)
            self.draw_piece(self.current_piece)
        else:
            game_over_txt = self.game_over_font.render("GAME OVER", True, (255, 50, 50))
            text_rect = game_over_txt.get_rect()
            grid_width = GRID_WIDTH * CELL_SIZE
            grid_height = GRID_HEIGHT * CELL_SIZE
            text_x = (grid_width // 2) - (text_rect.width // 2)
            text_y = (grid_height // 2) - (text_rect.height // 2)
            self.screen.blit(game_over_txt, (text_x, text_y))
            final_score_txt = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            score_rect = final_score_txt.get_rect()
            score_x = (grid_width // 2) - (score_rect.width // 2)
            score_y = text_y + text_rect.height + 20
            self.screen.blit(final_score_txt, (score_x, score_y))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.clock.tick(60)   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_input(event)
            self.update()
            self.draw()
        pygame.quit()
        sys.exit()
game = game()
game.run()