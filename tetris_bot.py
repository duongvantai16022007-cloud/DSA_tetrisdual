"""
Mô đun: tetris_bot.py
Mô tả: Triển khai logic Trí Tuệ Nhân Tạo (AI) để chơi game Tetris.
Cung cấp 3 cấp độ khó: EASY (Tập sự - phá ngẫu nhiên), HARD (Cao thủ - Lookahead 1 bằng Heuristic), 
và GOD (Siêu AI - Beam Search).
"""
import pygame
import copy
import random
import asset_manager as am
from tetris_dual import TetrisBoard, GRID_WIDTH, GRID_HEIGHT

def evaluate_grid_advanced(grid):
    """
    Phân tích một trạng thái lưới Tetris và trả về các chỉ số đặc trưng (features) 
    dùng để chấm điểm chất lượng của lưới đó.
    
    Args:
        grid (list[list]): Ma trận lưới đại diện cho trạng thái của game.
        
    Returns:
        tuple: Chứa 6 giá trị: (agg_height, holes, bumpiness, row_transitions, col_transitions, wells)
    """
    heights = [0] * GRID_WIDTH
    for c in range(GRID_WIDTH):
        for r in range(GRID_HEIGHT):
            if grid[r][c] != 0:
                heights[c] = GRID_HEIGHT - r
                break
                
    agg_height = sum(heights)
    holes = 0
    col_transitions = 0
    row_transitions = 0
    wells = 0
    for c in range(GRID_WIDTH):
        is_empty = True
        for r in range(GRID_HEIGHT):
            if grid[r][c] == 0 and heights[c] > GRID_HEIGHT - r:
                holes += 1
            current_is_empty = (grid[r][c] == 0)
            if current_is_empty != is_empty:
                col_transitions += 1
            is_empty = current_is_empty
    for r in range(GRID_HEIGHT):
        is_empty = True
        for c in range(GRID_WIDTH):
            current_is_empty = (grid[r][c] == 0)
            if current_is_empty != is_empty:
                row_transitions += 1
            is_empty = current_is_empty
    bumpiness = sum(abs(heights[c] - heights[c+1]) for c in range(GRID_WIDTH - 1))
    for c in range(GRID_WIDTH):
        for r in range(GRID_HEIGHT):
            if grid[r][c] == 0:
                left_filled = (c == 0 or grid[r][c-1] != 0)
                right_filled = (c == GRID_WIDTH - 1 or grid[r][c+1] != 0)
                if left_filled and right_filled:
                    depth = 1
                    nr = r + 1
                    while nr < GRID_HEIGHT and grid[nr][c] == 0:
                        depth += 1
                        nr += 1
                    wells += depth
                    break 
    return agg_height, holes, bumpiness, row_transitions, col_transitions, wells

def get_drop_state(piece, grid, test_x):
    """
    Giả lập thả 1 khối gạch (piece) xuống một cột cụ thể (test_x) trên lưới (grid).
    
    Args:
        piece (Block): Khối gạch hiện tại.
        grid (list[list]): Trạng thái lưới hiện tại.
        test_x (int): Tọa độ cột X cần thả thử.
        
    Returns:
        tuple or None: Trả về (sim_grid, lines_cleared) nếu thả thành công, trả về None nếu thả sai quy luật.
    """
    ghost = copy.deepcopy(piece)
    ghost.x = test_x
    ghost.y = 0
    for i, row in enumerate(ghost.matrix):
        for j, cell in enumerate(row):
            if cell != 0:
                gx = ghost.x + j
                gy = ghost.y + i
                if gx < 0 or gx >= GRID_WIDTH or gy >= GRID_HEIGHT or (gy >= 0 and grid[gy][gx] != 0):
                    return None 
                
    while True:
        ghost.y += 1
        col = False
        for i, row in enumerate(ghost.matrix):
            for j, cell in enumerate(row):
                if cell != 0:
                    gx = ghost.x + j
                    gy = ghost.y + i
                    if gy >= GRID_HEIGHT or (gy >= 0 and grid[gy][gx] != 0):
                        col = True; break
            if col: break
        if col:
            ghost.y -= 1
            break
    sim_grid = copy.deepcopy(grid)
    for i, row in enumerate(ghost.matrix):
        for j, cell in enumerate(row):
            if cell != 0 and ghost.y + i >= 0:
                sim_grid[ghost.y + i][ghost.x + j] = 1 
                
    # Ăn điểm
    lines_cleared = 0
    for i in range(GRID_HEIGHT):
        if 0 not in sim_grid[i]:
            lines_cleared += 1
            
    return sim_grid, lines_cleared

# ==========================================
# 1. BOT TẬP SỰ (EASY) - Tư duy "Có hàng là phá"
# ==========================================
class BotBoard(TetrisBoard):
    """
    Lớp điều khiển BOT cấp độ EASY.
    Kế thừa bảng lưới của người chơi 2, tự động ra quyết định bằng code không thông qua phím bấm.
    """
    def __init__(self, screen, offset_x, title):
        """Khởi tạo biến chứa logic tự động hóa di chuyển của BOT."""
        super().__init__(screen, offset_x, title, controls=None)
        self.target_x = 3
        self.target_rotation = 0
        self.bot_timer = 0
        self.bot_speed = 80 
        self.calculated = False 

    def calculate_best_move(self):
        """
        Duyệt tất cả khả năng xoay và cột (x) để đưa ra nước đi ưu tiên phá hàng nhất.
        Có tiêm thêm độ nhiễu (ngẫu nhiên) để tạo cảm giác "gà mờ".
        """
        states = []
        test_piece = copy.deepcopy(self.current_piece)
        for rot in range(4):
            for test_x in range(GRID_WIDTH):
                result = get_drop_state(test_piece, self.grid, test_x)
                if result:
                    sim_grid, lines = result
                    agg_height, holes, bumpiness, _, _, wells = evaluate_grid_advanced(sim_grid)
                    
                    #ƯU TIÊN PHÁ 1 HÀNG
                    score = (lines * 10000) - (agg_height * 10) - (holes * 20) - (bumpiness * 5)
                    
                    states.append({'score': score, 'lines_cleared': lines, 'x': test_x, 'rotation': rot})
            test_piece.rotate()
            
        if not states:
            self.target_x = 3; self.target_rotation = 0; self.calculated = True; return

        states.sort(key=lambda s: s['score'], reverse=True)
        
        best_move = states[0]
        
        # Tiêm nhiễu nhẹ (15%):
        # NẾU nước đi tốt nhất KHÔNG ăn được hàng nào, thi thoảng nó sẽ đi bừa 1 nước hơi lỗi (để giữ độ "gà").
        # Nhưng nếu nước đi tốt nhất CÓ THỂ ăn hàng, nó sẽ TẬP TRUNG 100% để phá hàng đó.
        if random.random() < 0.15 and len(states) > 2 and best_move['lines_cleared'] == 0:
            choice = random.choice(states[:3])
        else:
            choice = best_move
            
        self.target_x = choice['x']
        self.target_rotation = choice['rotation']
        self.calculated = True

    def update(self, dt):
        """
        Cập nhật di chuyển từng khung hình cho khối theo mục tiêu BOT đã tính toán (target_x, target_rotation).
        
        Args:
            dt (int): Thời gian Delta (mili giây) từ khung hình trước.
        """
        if self.game_over: return
        if not self.calculated: self.calculate_best_move()
        self.bot_timer += dt
        if self.bot_timer >= self.bot_speed:
            self.bot_timer = 0
            moved_x = False
            if self.current_piece.x < self.target_x:
                self.current_piece.x += 1
                if self.is_collision(self.current_piece): self.current_piece.x -= 1
                else: moved_x = True
            elif self.current_piece.x > self.target_x:
                self.current_piece.x -= 1
                if self.is_collision(self.current_piece): self.current_piece.x += 1
                else: moved_x = True

            if self.target_rotation > 0:
                self.current_piece.rotate()
                if self.is_collision(self.current_piece): self.current_piece.rotate_ccw()
                else: self.target_rotation -= 1
                return 

            if not moved_x and self.target_rotation == 0 and self.current_piece.x == self.target_x:
                ghost = self.get_ghost(); self.current_piece.y = ghost.y
                self.lock_piece(); self.clear_lines(); self.spawn_next(); self.calculated = False 
                return 
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.current_piece.y += 1
            if self.is_collision(self.current_piece):
                self.current_piece.y -= 1; self.lock_piece(); self.clear_lines(); self.spawn_next(); self.calculated = False
            self.fall_time = 0

# ==========================================
# 2. BOT CAO THỦ (HARD) - NHÌN TRƯỚC 1 VÀ SỬ DỤNG TRỌNG SỐ
# ==========================================
class HardBotBoard(BotBoard):
    """
    Lớp BOT cấp độ HARD.
    Sử dụng bộ trọng số chuẩn, phạt nặng vào lỗ hổng để giữ lưới gọn gàng.
    Tầm nhìn (Lookahead) 1 khối.
    """
    def __init__(self, screen, offset_x, title):
        super().__init__(screen, offset_x, title)
        self.bot_speed = 50 

    def _get_all_possible_states(self, piece, current_grid):
        """
        Sinh ra tất cả các trạng thái có thể của lưới với khối hiện tại.
        
        Args:
            piece (Block): Khối cần xem xét.
            current_grid (list[list]): Trạng thái lưới hiện tại.
            
        Returns:
            list[dict]: Danh sách chứa điểm số và tọa độ thả của mỗi trạng thái.
        """
        states = []
        test_piece = copy.deepcopy(piece)
        for rot in range(4):
            for test_x in range(GRID_WIDTH):
                result = get_drop_state(test_piece, current_grid, test_x)
                if result:
                    sim_grid, lines = result
                    agg_height, holes, bumpiness, row_t, col_t, wells = evaluate_grid_advanced(sim_grid)
                    #tăng trọng số cho việc phá lines
                    score = (lines ** 2) * 500  - (agg_height * 10.0) - (holes * 150.0) - (bumpiness * 10.0) - (row_t * 20.0) - (col_t * 20.0) - (wells * 50.0)
                    states.append({'score': score, 'lines': lines, 'x': test_x, 'rotation': rot, 'grid': sim_grid})
            test_piece.rotate()
            
        states.sort(key=lambda s: s['score'], reverse=True)
        return states

    def calculate_best_move(self):
        """Duyệt Lookahead 1 để tìm nước đi tốt nhất hiện tại."""
        states_d1 = self._get_all_possible_states(self.current_piece, self.grid)
        if not states_d1: 
            self.target_x = 3; self.target_rotation = 0; self.calculated = True; return
            
        best_move = states_d1[0]
        self.target_x = best_move['x']
        self.target_rotation = best_move['rotation']
        self.calculated = True

# ==========================================
# 3. BOT SIÊU AI (GOD) - Tầm nhìn rộng (Expanded Beam Search)
# ==========================================
class GodBotBoard(HardBotBoard):
    """
    Lớp BOT cấp độ GOD.
    Sử dụng kỹ thuật Beam Search để Lookahead 2 khối (khối hiện tại + khối NEXT).
    Tính toán cực kỳ thông minh để thiết lập Combo ăn nhiều hàng.
    """
    def __init__(self, screen, offset_x, title):
        """Thiết lập tốc độ và chiều rộng Beam Search."""
        super().__init__(screen, offset_x, title)
        self.bot_speed = 40 
        self.beam_width = 12 

    def calculate_best_move(self):
        """
        Duyệt Lookahead 2 khối: Khối hiện tại và Khối kế tiếp trong Beam (top K trạng thái tốt nhất).
        Mục đích tìm ra nước đi tốt nhất cho tương lai thay vì chỉ giải quyết tình hình hiện tại.
        """
        states_d1 = self._get_all_possible_states(self.current_piece, self.grid)
        if not states_d1: 
            self.target_x = 3; self.target_rotation = 0; self.calculated = True; return
            
        top_k = states_d1[:self.beam_width]
        best_score = -9999999
        best_move = None
        next_piece = self.next_queue[0]
        
        for s1 in top_k:
            states_d2 = self._get_all_possible_states(next_piece, s1['grid'])
            if not states_d2: 
                final_score = s1['score'] - 99999
            else: 
                # Đánh giá độ rủi ro tương lai: 
                # Nếu bước 1 ăn điểm nhưng bước 2 tạo ra lỗ hổng lớn, điểm final sẽ bị kéo xuống
                final_score = s1['score'] + (states_d2[0]['score'] * 0.8) # Ưu tiên hiện tại hơn tương lai 1 chút
                
            if final_score > best_score: 
                best_score = final_score
                best_move = s1

        if best_move: 
            self.target_x = best_move['x']
            self.target_rotation = best_move['rotation']
        else: 
            self.target_x = states_d1[0]['x']
            self.target_rotation = states_d1[0]['rotation']
        self.calculated = True

# ==========================================
# APP ĐIỀU PHỐI
# ==========================================
class TetrisBotApp():
    """
    Ứng dụng điều phối chế độ chơi 1 VS AI (Người chơi vs Máy).
    Vẽ 2 bảng lưới và cho phép 2 đối tượng cùng chạy đua.
    """
    def __init__(self, difficulty="EASY"):
        """
        Khởi tạo môi trường, Player 1 và gắn mô đun BOT vào bảng 2.
        
        Args:
            difficulty (str, optional): Cấp độ Bot ("EASY", "HARD", "GOD"). Mặc định "EASY".
        """
        pygame.init()
        pygame.key.set_repeat(200, 50)
        am.init_assets()
        am.play_bgm()
        
        self.board_w = GRID_WIDTH * am.CELL_SIZE + 280
        self.margin = 20
        self.screen_width = self.board_w * 2 + self.margin
        self.screen_height = GRID_HEIGHT * am.CELL_SIZE
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(f"Tetris 1 VS A.I ({difficulty}) - DSA Project")
        
        self.clock = pygame.time.Clock()
        self.winner_font = am.get_font(70)
        self.sub_font = am.get_font(30)
        self.winner = None
        self.win_sound_played = False

        p1_keys = {'LEFT': pygame.K_a, 'RIGHT': pygame.K_d, 'DOWN': pygame.K_s, 'UP': pygame.K_w, 'DROP': pygame.K_SPACE, 'HOLD': pygame.K_LSHIFT, 'CCW': pygame.K_q}
        self.p1 = TetrisBoard(self.screen, 0, "PLAYER 1 (WASD)", p1_keys)
        
        if difficulty == "GOD": self.bot = GodBotBoard(self.screen, self.board_w + self.margin, "A.I BOT (SIÊU AI)")
        elif difficulty == "HARD": self.bot = HardBotBoard(self.screen, self.board_w + self.margin, "A.I BOT (CAO THỦ)")
        else: self.bot = BotBoard(self.screen, self.board_w + self.margin, "A.I BOT (TẬP SỰ)")

    def run(self):
        """Khởi chạy vòng lặp chính của chế độ PvE."""
        running = True
        while running:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False 
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False 
                if self.winner is None: self.p1.handle_input(event)

            if self.winner is None:
                self.p1.update(dt); self.bot.update(dt) 
                if self.p1.game_over and self.bot.game_over:
                    if self.p1.score > self.bot.score: self.winner = "PLAYER 1 WINS!"
                    elif self.bot.score > self.p1.score: self.winner = "BOT WINS! (A.I Thắng)"
                    else: self.winner = "DRAW! (HÒA)"

            if am.ASSETS['bg']:
                bg_scaled = pygame.transform.smoothscale(am.ASSETS['bg'], (self.screen_width, self.screen_height))
                self.screen.blit(bg_scaled, (0, 0))
                overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 170)); self.screen.blit(overlay, (0, 0))
            else: self.screen.fill((15, 15, 15))
                
            pygame.draw.line(self.screen, (80, 80, 80), (self.board_w + 10, 0), (self.board_w + 10, self.screen_height), 2)
            self.p1.draw(); self.bot.draw()

            if self.winner:
                if not self.win_sound_played:
                    am.stop_bgm()
                    am.play_sfx('win')
                    self.win_sound_played = True
                    
                overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180)); self.screen.blit(overlay, (0, 0))
                am.draw_text(self.screen, self.winner, self.winner_font, (255, 215, 0), 
                             (self.screen_width // 2 - self.winner_font.size(self.winner)[0]//2, self.screen_height // 2 - 50))
                am.draw_text(self.screen, "Nhấn ESC để quay về Menu", self.sub_font, (255, 255, 255), 
                             (self.screen_width // 2 - self.sub_font.size("Nhấn ESC để quay về Menu")[0]//2, self.screen_height // 2 + 30))

            pygame.display.flip()

if __name__ == "__main__":
    TetrisBotApp(difficulty="GOD").run()
    pygame.quit()