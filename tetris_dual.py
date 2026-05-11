"""
Mô đun: tetris_dual.py
Mô tả: Quản lý chế độ 2 người chơi cục bộ (PvP). Cung cấp khả năng vận hành
hai bảng Tetris độc lập trên cùng một màn hình (Split-screen).
"""
import pygame
import copy
import random
import asset_manager as am
from main import Block, Particle, SHAPES, GRID_WIDTH, GRID_HEIGHT

class TetrisBoard():
    """
    Lớp đại diện cho một bảng lưới Tetris độc lập dành cho một người chơi.
    Sử dụng lại logic khối của main.py nhưng cho phép tùy biến phím điều khiển và tọa độ vẽ.
    """
    def __init__(self, screen, offset_x, title, controls):
        """
        Khởi tạo một bảng Tetris.
        
        Args:
            screen (pygame.Surface): Bề mặt vẽ.
            offset_x (int): Độ dời theo trục X để bảng vẽ sang bên phải/trái.
            title (str): Tiêu đề tên người chơi (VD: "PLAYER 1").
            controls (dict): Dictionary định nghĩa các phím điều khiển (LEFT, RIGHT, DOWN, UP, DROP, HOLD, CCW).
        """
        self.screen = screen
        self.offset_x = offset_x
        self.title = title
        self.controls = controls
        self.font = am.get_font(24)
        self.game_over_font = am.get_font(50)
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.game_over = False
        self.level = 1
        self.lines_cleared_total = 0 
        self.base_fall_speed = 300 
        self.next_queue = []
        self.fill_queue()
        self.current_piece = self.next_queue.pop(0)
        self.held_piece = None
        self.can_swap = True 
        self.fall_time = 0
        self.fall_speed = self.base_fall_speed
        self.particles = [] 

    def fill_queue(self):
        """Duy trì danh sách 4 khối ngẫu nhiên tiếp theo."""
        while len(self.next_queue) < 4: self.next_queue.append(Block(random.choice(list(SHAPES.keys()))))

    def is_collision(self, nblock: Block):
        """Kiểm tra va chạm giữa khối nblock và bảng."""
        for i, row in enumerate(nblock.matrix):
            for j, cell in enumerate(row):
                if cell != 0:
                    x = nblock.x + j; y = nblock.y + i
                    if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT or (y >= 0 and self.grid[y][x] != 0): return True
        return False

    def lock_piece(self):
        """Đóng băng khối hiện tại lên bảng lưới vĩnh viễn."""
        for i, row in enumerate(self.current_piece.matrix):
            for j, cell in enumerate(row):
                if cell != 0 and self.current_piece.y + i >= 0:
                    self.grid[self.current_piece.y + i][self.current_piece.x + j] = self.current_piece.name

    def clear_lines(self):
        """Xóa hàng, sinh hạt vỡ và tính điểm số, mức độ (Level)."""
        line_count = 0; i = GRID_HEIGHT - 1
        while i >= 0:
            if 0 not in self.grid[i]:
                line_count += 1
                for c in range(GRID_WIDTH):
                    shape_name = self.grid[i][c]
                    color = am.COLORS.get(shape_name, (255, 255, 255))
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
        """Lấy phiên bản bóng mờ dự đoán điểm chạm của khối hiện tại."""
        ghost = copy.deepcopy(self.current_piece)
        while not self.is_collision(ghost): ghost.y += 1
        ghost.y -= 1; return ghost

    def spawn_next(self):
        """Sinh khối tiếp theo và khôi phục trạng thái can_swap (cho phép Hold)."""
        self.fill_queue(); self.current_piece = self.next_queue.pop(0); self.can_swap = True
        if self.is_collision(self.current_piece): self.game_over = True

    def handle_input(self, event):
        """
        Xử lý input dựa vào controls mapping cung cấp riêng cho người chơi đó.
        
        Args:
            event (pygame.event.Event): Sự kiện từ bàn phím.
        """
        if event.type == pygame.KEYDOWN and not self.game_over:
            if self.controls is None: return 
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
                if self.is_collision(self.current_piece): self.current_piece.rotate_ccw()
            elif 'CCW' in self.controls and event.key == self.controls['CCW']:
                self.current_piece.rotate_ccw()
                if self.is_collision(self.current_piece): self.current_piece.rotate()
            elif event.key == self.controls['DROP']:
                ghost = self.get_ghost(); self.current_piece.y = ghost.y
                self.lock_piece(); self.clear_lines(); self.spawn_next()
            elif event.key == self.controls['HOLD'] and self.can_swap:
                if self.held_piece is None:
                    self.held_piece = self.current_piece; self.spawn_next()
                else:
                    self.current_piece, self.held_piece = self.held_piece, self.current_piece
                    self.current_piece.x = 3; self.current_piece.y = 0
                    self.current_piece.matrix = copy.deepcopy(SHAPES[self.current_piece.name])
                self.can_swap = False

    def update(self, dt):
        """
        Cập nhật trọng lực (chạy bộ đếm timer theo dt) và hoạt ảnh của các hạt.
        
        Args:
            dt (int): Delta time.
        """
        if self.game_over: return
        for p in self.particles[:]:
            p.update()
            if p.lifetime <= 0 or p.size <= 0: self.particles.remove(p)
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.current_piece.y += 1
            if self.is_collision(self.current_piece):
                self.current_piece.y -= 1; self.lock_piece(); self.clear_lines(); self.spawn_next()
            self.fall_time = 0

    def draw_piece(self, piece, start_x=0, start_y=0, is_ghost=False, scale=1.0):
        """Vẽ khối theo độ dời offset_x cố định của bảng."""
        for i, row in enumerate(piece.matrix):
            for j, cell in enumerate(row):
                if cell != 0:
                    x = self.offset_x + start_x + (piece.x + j) * (am.CELL_SIZE * scale)
                    y = start_y + (piece.y + i) * (am.CELL_SIZE * scale)
                    if is_ghost:
                        pygame.draw.rect(self.screen, piece.color, pygame.Rect(x, y, am.CELL_SIZE * scale, am.CELL_SIZE * scale), 2)
                    else:
                        img = am.ASSETS['blocks'][piece.name]
                        if scale != 1.0: img = pygame.transform.scale(img, (int(am.CELL_SIZE * scale), int(am.CELL_SIZE * scale)))
                        self.screen.blit(img, (x, y))

    def draw(self):
        """Vẽ toàn bộ bảng lưới bao gồm nền, khối đang rơi, UI, ... lên màn hình."""
        grid_rect = pygame.Rect(self.offset_x, 0, GRID_WIDTH * am.CELL_SIZE, GRID_HEIGHT * am.CELL_SIZE)
        pygame.draw.rect(self.screen, (50, 50, 50), grid_rect, 2)
        
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                if self.grid[r][c] == 0:
                    pygame.draw.rect(self.screen, (35, 35, 35), pygame.Rect(self.offset_x + c * am.CELL_SIZE, r * am.CELL_SIZE, am.CELL_SIZE, am.CELL_SIZE), 1)
                else:
                    shape_name = self.grid[r][c]
                    self.screen.blit(am.ASSETS['blocks'][shape_name], (self.offset_x + c * am.CELL_SIZE, r * am.CELL_SIZE))

        panel_x = self.offset_x + GRID_WIDTH * am.CELL_SIZE + 20
        am.draw_text(self.screen, self.title, self.font, (255, 255, 0), (panel_x, 10))
        am.draw_text(self.screen, f"SCORE: {self.score}", self.font, (0, 255, 255), (panel_x, 50))
        am.draw_text(self.screen, f"LEVEL: {self.level}", self.font, (255, 165, 0), (panel_x, 80))

        pygame.draw.rect(self.screen, (30, 30, 30, 180), (panel_x - 10, 120, 180, 250))
        am.draw_text(self.screen, "NEXT:", self.font, (255, 255, 255), (panel_x, 130))
        p_next1 = copy.deepcopy(self.next_queue[0]); p_next1.x = 0; p_next1.y = 0
        self.draw_piece(p_next1, start_x=GRID_WIDTH * am.CELL_SIZE + 50, start_y=170, scale=0.7)
        p_next2 = copy.deepcopy(self.next_queue[1]); p_next2.x = 0; p_next2.y = 0
        self.draw_piece(p_next2, start_x=GRID_WIDTH * am.CELL_SIZE + 50, start_y=260, scale=0.7)

        pygame.draw.rect(self.screen, (30, 30, 30, 180), (panel_x - 10, 390, 180, 120))
        am.draw_text(self.screen, "HOLD:", self.font, (255, 255, 255), (panel_x, 400))
        if self.held_piece:
            p_hold = copy.deepcopy(self.held_piece); p_hold.x = 0; p_hold.y = 0
            self.draw_piece(p_hold, start_x=GRID_WIDTH * am.CELL_SIZE + 50, start_y=430, scale=0.7)

        for p in self.particles: p.draw(self.screen, self.offset_x)

        if not self.game_over:
            self.draw_piece(self.get_ghost(), is_ghost=True)
            self.draw_piece(self.current_piece)
        else:
            msg = self.game_over_font.render("OVER", True, (255, 50, 50))
            self.screen.blit(msg, msg.get_rect(center=(self.offset_x + (GRID_WIDTH * am.CELL_SIZE)//2, (GRID_HEIGHT * am.CELL_SIZE)//2)))

class TetrisDualApp():
    """
    Ứng dụng điều phối chế độ 2 người chơi nội bộ (PvP).
    Chạy 2 TetrisBoard riêng biệt trên cùng 1 vòng lặp.
    """
    def __init__(self):
        """Khởi tạo màn hình đôi"""
        pygame.init()
        pygame.key.set_repeat(200, 50) 
        am.init_assets()
        am.play_bgm()
        
        self.board_w = GRID_WIDTH * am.CELL_SIZE + 250
        self.margin = 20
        self.screen_width = self.board_w * 2 + self.margin
        self.screen_height = GRID_HEIGHT * am.CELL_SIZE
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Tetris Dual PvP - DSA Project")
        
        self.clock = pygame.time.Clock()
        self.winner_font = am.get_font(70)
        self.sub_font = am.get_font(30)

        p1_keys = {'LEFT': pygame.K_a, 'RIGHT': pygame.K_d, 'DOWN': pygame.K_s, 'UP': pygame.K_w, 'DROP': pygame.K_SPACE, 'HOLD': pygame.K_LSHIFT, 'CCW': pygame.K_q}
        p2_keys = {'LEFT': pygame.K_LEFT, 'RIGHT': pygame.K_RIGHT, 'DOWN': pygame.K_DOWN, 'UP': pygame.K_UP, 'DROP': pygame.K_RETURN, 'HOLD': pygame.K_RSHIFT, 'CCW': pygame.K_RCTRL}

        self.p1 = TetrisBoard(self.screen, 0, "PLAYER 1 (WASD)", p1_keys)
        self.p2 = TetrisBoard(self.screen, self.board_w + self.margin, "PLAYER 2 (Arrows)", p2_keys)
        self.winner = None
        self.win_sound_played = False

    def run(self):
        """Khởi chạy vòng lặp chính của chế độ PvP."""
        running = True
        while running:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False 
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False 
                if self.winner is None:
                    self.p1.handle_input(event)
                    self.p2.handle_input(event)

            if self.winner is None:
                self.p1.update(dt)
                self.p2.update(dt)
                if self.p1.game_over and self.p2.game_over:
                    if self.p1.score > self.p2.score: self.winner = "PLAYER 1 WINS!"
                    elif self.p2.score > self.p1.score: self.winner = "PLAYER 2 WINS!"
                    else: self.winner = "DRAW! (HÒA)"

            if am.ASSETS['bg']:
                bg_scaled = pygame.transform.smoothscale(am.ASSETS['bg'], (self.screen_width, self.screen_height))
                self.screen.blit(bg_scaled, (0, 0))
                overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 170))
                self.screen.blit(overlay, (0, 0))
            else: self.screen.fill((15, 15, 15))
                
            pygame.draw.line(self.screen, (80, 80, 80), (self.board_w + 10, 0), (self.board_w + 10, self.screen_height), 2)
            self.p1.draw()
            self.p2.draw()

            if self.winner:
                if not self.win_sound_played:
                    am.stop_bgm()
                    am.play_sfx('win')
                    self.win_sound_played = True
                    
                overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))
                am.draw_text(self.screen, self.winner, self.winner_font, (255, 215, 0), 
                             (self.screen_width//2 - self.winner_font.size(self.winner)[0]//2, self.screen_height//2 - 50))
                am.draw_text(self.screen, "Nhấn ESC để quay về Menu", self.sub_font, (255, 255, 255), 
                             (self.screen_width//2 - self.sub_font.size("Nhấn ESC để quay về Menu")[0]//2, self.screen_height//2 + 30))

            pygame.display.flip()

if __name__ == "__main__":
    TetrisDualApp().run()
    pygame.quit()