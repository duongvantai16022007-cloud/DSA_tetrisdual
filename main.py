"""
Mô đun: main.py
Mô tả: Chứa logic cốt lõi cho chế độ 1 người chơi (Solo). 
Định nghĩa các lớp cơ sở bao gồm Particle (hiệu ứng), Block (khối hình) và Game (vòng lặp chính).
"""
import pygame
import copy
import random
import asset_manager as am

SHAPES = {
    'I': [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
    'J': [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
    'L': [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
    'O': [[1, 1], [1, 1]], 
    'S': [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
    'T': [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
    'Z': [[1, 1, 0], [0, 1, 1], [0, 0, 0]]
}

GRID_WIDTH = 10
GRID_HEIGHT = 20

class Particle:
    """
    Lớp quản lý hiệu ứng hạt vỡ ra khi người chơi ăn điểm (xóa hàng).
    """
    def __init__(self, x, y, color):
        """
        Khởi tạo một hạt (particle) với vị trí, màu sắc, vận tốc và tuổi thọ ngẫu nhiên.
        """
        self.x = x; self.y = y; self.color = color
        self.vx = random.uniform(-4, 4); self.vy = random.uniform(-6, -2) 
        self.gravity = 0.3; self.size = random.randint(5, 10); self.lifetime = random.randint(30, 50)
        
    def update(self):
        """
        Cập nhật vị trí, kích thước và tuổi thọ của hạt theo mỗi khung hình.
        Áp dụng trọng lực để tạo hiệu ứng rơi.
        """
        self.x += self.vx; self.y += self.vy; self.vy += self.gravity; self.size -= 0.2; self.lifetime -= 1      
        
    def draw(self, screen, offset_x=0):
        """
        Vẽ hạt lên màn hình nếu hạt vẫn còn tồn tại (size > 0).
        """
        if self.size > 0:
            pygame.draw.rect(screen, self.color, pygame.Rect(offset_x + self.x, self.y, int(self.size), int(self.size)))

class Block():
    """
    Lớp đại diện cho một khối Tetromino di chuyển trên lưới.
    """
    def __init__(self, shapes):
        """
        Khởi tạo khối dựa trên tên hình dạng cung cấp.
        
        Args:
            shapes (str): Chữ cái đại diện cho khối ('I', 'J', 'L', 'O', 'S', 'T', 'Z').
        """
        self.name = shapes 
        self.matrix = copy.deepcopy(SHAPES[shapes])
        self.color = am.COLORS[shapes] 
        self.x = 3; self.y = 0  

    def rotate(self):
        """
        Xoay ma trận của khối theo chiều kim đồng hồ (90 độ).
        """
        n = len(self.matrix)
        for i in range(n):
            for j in range(i, n): self.matrix[i][j], self.matrix[j][i] = self.matrix[j][i], self.matrix[i][j]
        for i in range(n): self.matrix[i].reverse()

    def rotate_ccw(self):
        """
        Xoay ma trận của khối ngược chiều kim đồng hồ (-90 độ).
        """
        n = len(self.matrix)
        for i in range(n): self.matrix[i].reverse()
        for i in range(n):
            for j in range(i, n): self.matrix[i][j], self.matrix[j][i] = self.matrix[j][i], self.matrix[i][j]

class Game():
    """
    Lớp chính điều khiển chế độ chơi Tetris một người (Solo).
    Quản lý vòng lặp game, điểm số, mức độ, và tương tác của người chơi.
    """
    def __init__(self):
        """Khởi tạo màn hình game, biến môi trường, và hàng đợi khối kế tiếp."""
        pygame.init()
        pygame.key.set_repeat(200, 50) 
        am.init_assets()
        am.play_bgm()
        
        self.screen_width = GRID_WIDTH * am.CELL_SIZE + 200
        self.screen_height = GRID_HEIGHT * am.CELL_SIZE
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Tetris Solo - DSA Project")
        
        self.font = am.get_font(28)
        self.game_over_font = am.get_font(60)
        self.clock = pygame.time.Clock()

        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0; self.game_over = False

        self.level = 1
        self.lines_cleared_total = 0 
        self.base_fall_speed = 200 

        self.next_queue = []; self.fill_queue(); self.current_piece = self.next_queue.pop(0)
        self.held_piece = None; self.can_swap = True
        self.fall_time = 0; self.fall_speed = self.base_fall_speed; self.particles = []

    def random_block(self): 
        """Sinh ra một khối ngẫu nhiên mới."""
        return Block(random.choice(list(SHAPES.keys())))
        
    def fill_queue(self):
        """Đảm bảo hàng đợi luôn có đủ 4 khối hiển thị phần 'NEXT'."""
        while len(self.next_queue) < 4: self.next_queue.append(self.random_block())

    def is_collision(self, nblock: Block):
        """
        Kiểm tra va chạm giữa một khối và biên của lưới hoặc các khối đã khóa dưới lưới.
        
        Args:
            nblock (Block): Khối cần kiểm tra.
            
        Returns:
            bool: True nếu có va chạm, ngược lại False.
        """
        for i, row in enumerate(nblock.matrix):
            for j, cell in enumerate(row):
                if cell != 0:
                    x = nblock.x + j; y = nblock.y + i
                    if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT or (y >= 0 and self.grid[y][x] != 0): return True
        return False

    def lock_piece(self):
        """
        Cố định (khóa) khối hiện tại vào lưới vĩnh viễn khi nó đã chạm đáy.
        """
        for i, row in enumerate(self.current_piece.matrix):
            for j, cell in enumerate(row):
                if cell != 0 and self.current_piece.y + i >= 0:
                    self.grid[self.current_piece.y + i][self.current_piece.x + j] = self.current_piece.name

    def clear_score(self):
        """
        Quét lưới để tìm và xóa các hàng đã được lấp đầy.
        Tạo hiệu ứng vỡ hạt, tính toán điểm số và cấp độ (Level) mới.
        """
        line_count = 0; i = GRID_HEIGHT - 1
        while i >= 0:
            if 0 not in self.grid[i]:
                line_count += 1
                for c in range(GRID_WIDTH):
                    shape_key = self.grid[i][c]
                    color = am.COLORS.get(shape_key, (255, 255, 255))
                    for _ in range(5):
                        self.particles.append(Particle(c * am.CELL_SIZE + am.CELL_SIZE // 2, i * am.CELL_SIZE + am.CELL_SIZE // 2, color))
                del self.grid[i]; self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            else: i -= 1
                
        if line_count > 0:
            am.play_sfx('clear')
            old_level = self.level 
            self.lines_cleared_total += line_count
            self.level = (self.lines_cleared_total // 10) + 1
            if self.level > old_level: am.change_background()
            
            self.fall_speed = max(50, self.base_fall_speed - (self.level - 1) * 25)
            score_table = [0, 100, 300, 500, 1200]
            if line_count > 4: line_count = 4
            self.score += score_table[line_count] * self.level

    def get_ghost(self):
        """
        Tạo và trả về một khối 'Bóng' (Ghost piece) đại diện cho vị trí rơi dự kiến.
        
        Returns:
            Block: Bản sao của khối hiện tại ở vị trí rơi thấp nhất có thể.
        """
        ghost = copy.deepcopy(self.current_piece)
        while not self.is_collision(ghost): ghost.y += 1
        ghost.y -= 1; return ghost

    def spawn_next(self):
        """
        Lấy khối tiếp theo từ hàng đợi làm khối hiện tại.
        Kiểm tra va chạm để xác định trạng thái Game Over.
        """
        self.fill_queue(); self.current_piece = self.next_queue.pop(0); self.can_swap = True
        if self.is_collision(self.current_piece): self.game_over = True

    def handle_input(self, event):
        """
        Xử lý sự kiện bàn phím từ người chơi để điều khiển khối.
        
        Args:
            event (pygame.event.Event): Sự kiện từ Pygame.
        """
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
                if self.is_collision(self.current_piece): self.current_piece.rotate_ccw()
            elif event.key == pygame.K_z: 
                self.current_piece.rotate_ccw()
                if self.is_collision(self.current_piece): self.current_piece.rotate()
            elif event.key == pygame.K_SPACE:
                ghost = self.get_ghost(); self.current_piece.y = ghost.y
                self.lock_piece(); self.clear_score(); self.spawn_next()
            elif (event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_c]) and self.can_swap:
                if self.held_piece is None:
                    self.held_piece = self.current_piece; self.spawn_next() 
                else:
                    self.current_piece, self.held_piece = self.held_piece, self.current_piece
                    self.current_piece.x = 3; self.current_piece.y = 0
                    self.current_piece.matrix = copy.deepcopy(SHAPES[self.current_piece.name])
                self.can_swap = False

    def update(self):
        """
        Cập nhật logic game theo thời gian, xử lý trọng lực thả khối rơi xuống.
        Cập nhật danh sách các hạt hiệu ứng.
        """
        if self.game_over: return 
        for p in self.particles[:]:
            p.update()
            if p.lifetime <= 0 or p.size <= 0: self.particles.remove(p)
        self.fall_time += self.clock.get_rawtime()
        if self.fall_time >= self.fall_speed:
            self.current_piece.y += 1
            if self.is_collision(self.current_piece):
                self.current_piece.y -= 1; self.lock_piece(); self.clear_score(); self.spawn_next()
            self.fall_time = 0

    def draw_piece(self, piece, start_x=0, start_y=0, is_ghost=False, scale=1.0):
        """
        Vẽ một khối (Block) lên màn hình. Hỗ trợ thay đổi kích thước và vẽ dạng bóng (ghost).
        
        Args:
            piece (Block): Khối cần vẽ.
            start_x (int, optional): Tọa độ X bắt đầu. Mặc định 0.
            start_y (int, optional): Tọa độ Y bắt đầu. Mặc định 0.
            is_ghost (bool, optional): Nếu là True, sẽ vẽ khối dạng viền rỗng.
            scale (float, optional): Hệ số thu phóng khối. Mặc định 1.0.
        """
        for i, row in enumerate(piece.matrix):
            for j, cell in enumerate(row):
                if cell != 0:
                    x = start_x + (piece.x + j) * (am.CELL_SIZE * scale)
                    y = start_y + (piece.y + i) * (am.CELL_SIZE * scale)
                    if is_ghost:
                        pygame.draw.rect(self.screen, piece.color, pygame.Rect(x, y, am.CELL_SIZE * scale, am.CELL_SIZE * scale), 2)
                    else:
                        img = am.ASSETS['blocks'][piece.name]
                        if scale != 1.0: img = pygame.transform.scale(img, (int(am.CELL_SIZE * scale), int(am.CELL_SIZE * scale)))
                        self.screen.blit(img, (x, y))

    def draw(self):
        """
        Vẽ toàn bộ khung cảnh của game bao gồm: background, bảng lưới, UI (Score, Level), 
        hàng đợi khối (NEXT), khối đang giữ (HOLD), các hạt hiệu ứng và thông báo GAME OVER.
        """
        if am.ASSETS['bg']:
            bg_scaled = pygame.transform.smoothscale(am.ASSETS['bg'], (self.screen_width, self.screen_height))
            self.screen.blit(bg_scaled, (0, 0))
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
        else: self.screen.fill((20, 20, 20)) 

        am.draw_text(self.screen, f"SCORE: {self.score}", self.font, (0, 255, 255), (GRID_WIDTH * am.CELL_SIZE + 20, 20))
        am.draw_text(self.screen, f"LEVEL: {self.level}", self.font, (255, 165, 0), (GRID_WIDTH * am.CELL_SIZE + 20, 60))

        pygame.draw.rect(self.screen, (30, 30, 30, 180), (GRID_WIDTH * am.CELL_SIZE + 10, 100, 180, 250))
        am.draw_text(self.screen, "NEXT:", self.font, (255, 255, 255), (GRID_WIDTH * am.CELL_SIZE + 20, 110))
        
        p_next1 = copy.deepcopy(self.next_queue[0]); p_next1.x = 0; p_next1.y = 0
        self.draw_piece(p_next1, start_x=GRID_WIDTH * am.CELL_SIZE + 50, start_y=160, scale=0.7)
        p_next2 = copy.deepcopy(self.next_queue[1]); p_next2.x = 0; p_next2.y = 0
        self.draw_piece(p_next2, start_x=GRID_WIDTH * am.CELL_SIZE + 50, start_y=250, scale=0.7)

        pygame.draw.rect(self.screen, (30, 30, 30, 180), (GRID_WIDTH * am.CELL_SIZE + 10, 380, 180, 120))
        am.draw_text(self.screen, "HOLD:", self.font, (255, 255, 255), (GRID_WIDTH * am.CELL_SIZE + 20, 390))
        if self.held_piece:
            hold_preview = copy.deepcopy(self.held_piece); hold_preview.x = 0; hold_preview.y = 0
            self.draw_piece(hold_preview, start_x=GRID_WIDTH * am.CELL_SIZE + 50, start_y=420, scale=0.7)

        pygame.draw.line(self.screen, (100, 100, 100), (GRID_WIDTH * am.CELL_SIZE, 0), (GRID_WIDTH * am.CELL_SIZE, GRID_HEIGHT * am.CELL_SIZE), 2)
        
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                if self.grid[r][c] == 0:
                    pygame.draw.rect(self.screen, (50, 50, 50), pygame.Rect(c * am.CELL_SIZE, r * am.CELL_SIZE, am.CELL_SIZE, am.CELL_SIZE), 1) 
                else:
                    self.screen.blit(am.ASSETS['blocks'][self.grid[r][c]], (c * am.CELL_SIZE, r * am.CELL_SIZE))

        for p in self.particles: p.draw(self.screen)

        if not self.game_over:
            self.draw_piece(self.get_ghost(), is_ghost=True)
            self.draw_piece(self.current_piece)
        else:
            msg = self.game_over_font.render("GAME OVER", True, (255, 50, 50))
            self.screen.blit(msg, msg.get_rect(center=(self.screen_width//2, self.screen_height//2)))
            score_txt = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_txt, score_txt.get_rect(center=(self.screen_width//2, self.screen_height//2 + 50)))

        pygame.display.flip()

    def run(self):
        """
        Khởi chạy vòng lặp chính của chế độ chơi game.
        Xử lý sự kiện, cập nhật logic và vẽ lại khung hình ở tần số 60 FPS.
        """
        running = True
        while running:
            self.clock.tick(60) 
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False 
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False 
                self.handle_input(event)
            self.update()
            self.draw()
        return 

if __name__ == "__main__":
    Game().run()
    pygame.quit()