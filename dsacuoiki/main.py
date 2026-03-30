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
class game():
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('Consolas', 24, bold=True)
        window_width = GRID_WIDTH * CELL_SIZE + 200
        window_height = GRID_HEIGHT * CELL_SIZE

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
            for j, cell in (row):
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
            if 0 not in self.grid:
                line +=1
                del self.grid[i]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            else:
                i -= 1
        if line > 0:
            self.score += (line * 100) * line
    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()
"""""""
game = game()
game.run()