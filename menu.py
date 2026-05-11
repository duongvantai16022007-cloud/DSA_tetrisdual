"""
Mô đun: menu.py
Mô tả: Controller tổng để điều hướng game. Bao gồm giao diện Menu chính, 
tích hợp thanh trượt thay đổi âm lượng, và các menu phụ (chọn độ khó BOT).
"""
import pygame
import sys
import asset_manager as am
from main import Game
from tetris_dual import TetrisDualApp
from tetris_bot import TetrisBotApp

class MainMenu():
    """
    Lớp quản lý và hiển thị các Menu để người chơi có thể chọn chế độ chơi mong muốn
    hoặc tinh chỉnh hệ thống (âm lượng).
    """
    def __init__(self):
        """Khởi tạo Menu nền tảng, thiết lập các font chữ và các biến phục vụ kéo thả UI."""
        pygame.init()
        am.init_assets()
        
        self.screen_width = 600
        self.screen_height = 800 
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("UIT Tetris - DSA Project")
        
        self.title_font = am.get_font(70)
        self.btn_font = am.get_font(35)
        self.small_font = am.get_font(20)
        am.play_bgm()
        
        # Biến trạng thái kéo thanh trượt
        self.dragging_vol = False

    def draw_button(self, text, y_pos, mouse_pos):
        """
        Vẽ một nút bấm cơ bản tại vị trí Y được chỉ định, hỗ trợ hiệu ứng hover chuột.
        
        Args:
            text (str): Chữ hiển thị trên nút.
            y_pos (int): Tọa độ Y để đặt nút.
            mouse_pos (tuple): Vị trí hiện tại của chuột (để bắt va chạm hover).
            
        Returns:
            pygame.Rect: Hình chữ nhật va chạm (rect) đại diện cho kích thước nút.
        """
        btn_width = 400; btn_height = 70
        btn_x = (self.screen_width - btn_width) // 2
        btn_rect = pygame.Rect(btn_x, y_pos, btn_width, btn_height)

        if btn_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, (100, 100, 150), btn_rect, border_radius=15)  
        else:
            pygame.draw.rect(self.screen, (40, 40, 60), btn_rect, border_radius=15)     
        pygame.draw.rect(self.screen, (255, 255, 255), btn_rect, 3, border_radius=15)

        text_x = btn_rect.centerx - self.btn_font.size(text)[0] // 2
        text_y = btn_rect.centery - self.btn_font.size(text)[1] // 2
        am.draw_text(self.screen, text, self.btn_font, (255, 255, 255), (text_x, text_y))
        
        return btn_rect

    def draw_audio_slider(self, mouse_pos):
        """
        Vẽ cụm UI âm lượng bao gồm biểu tượng Mute và thanh trượt (slider).
        
        Args:
            mouse_pos (tuple): Vị trí con trỏ chuột trên màn hình.
            
        Returns:
            tuple: (Nút Mute Rect, Vùng chạm Slider Rect, Tọa độ X của Slider, Chiều dài Slider).
        """
        start_x = self.screen_width - 240
        y_pos = 20

        # VẼ ICON HOẶC NÚT MUTE
        btn_mute_rect = pygame.Rect(start_x, y_pos - 5, 40, 40)
        if 'music' in am.ASSETS['ui']:
            # Nếu có icon, chèn icon (hiệu ứng mờ khi tắt tiếng)
            icon = am.ASSETS['ui']['music'].copy()
            if am.is_muted: icon.set_alpha(100) # Làm mờ icon nếu Mute
            self.screen.blit(icon, btn_mute_rect)
        else:
            # Backup nếu không load được ảnh
            pygame.draw.rect(self.screen, (180, 50, 50) if am.is_muted else (40, 40, 60), btn_mute_rect, border_radius=5)
            am.draw_text(self.screen, "M", self.small_font, (255, 255, 255), (start_x + 10, y_pos + 5))

        # CẤU HÌNH THANH TRƯỢT
        slider_x = start_x + 50
        slider_y = y_pos + 10
        slider_w = 120
        slider_h = 10

        # 1. Vẽ track nền (Màu tối)
        track_rect = pygame.Rect(slider_x, slider_y, slider_w, slider_h)
        pygame.draw.rect(self.screen, (80, 80, 80), track_rect, border_radius=5)

        # 2. Vẽ phần âm lượng đã đầy (Màu sáng)
        current_vol = 0 if am.is_muted else am.global_vol
        fill_w = int(current_vol * slider_w)
        fill_rect = pygame.Rect(slider_x, slider_y, fill_w, slider_h)
        pygame.draw.rect(self.screen, (0, 255, 255), fill_rect, border_radius=5)

        # 3. Vẽ Cục Tròn (Handle)
        handle_x = slider_x + fill_w
        handle_y = slider_y + slider_h // 2
        
        # Nếu đang kéo rê chuột hoặc rê chuột ngang qua thì làm sáng cục tròn lên
        click_rect = pygame.Rect(slider_x - 10, slider_y - 10, slider_w + 20, slider_h + 20)
        handle_color = (255, 255, 255) if (self.dragging_vol or click_rect.collidepoint(mouse_pos)) else (200, 200, 200)
        pygame.draw.circle(self.screen, handle_color, (handle_x, handle_y), 8)

        # 4. Hiển thị phần trăm %
        vol_pct = int(current_vol * 100)
        am.draw_text(self.screen, f"{vol_pct}%", self.small_font, (255, 255, 255), (slider_x + slider_w + 15, y_pos))

        return btn_mute_rect, click_rect, slider_x, slider_w

    def run_bot_menu(self):
        """
        Hiển thị và xử lý Menu phụ (Sub-Menu) cho phép người chơi chọn độ khó của BOT
        trước khi vào chế độ 1 VS AI.
        """
        running_sub = True
        self.dragging_vol = False
        while running_sub:
            mouse_pos = pygame.mouse.get_pos()
            
            if am.ASSETS['bg']:
                bg_scaled = pygame.transform.smoothscale(am.ASSETS['bg'], (self.screen_width, self.screen_height))
                self.screen.blit(bg_scaled, (0, 0))
                overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150)); self.screen.blit(overlay, (0, 0))
            else:
                self.screen.fill((20, 30, 40))

            title_text = "CHỌN ĐỐI THỦ"
            am.draw_text(self.screen, title_text, self.title_font, (255, 215, 0), 
                         (self.screen_width//2 - self.title_font.size(title_text)[0]//2, 120))

            btn_mute, slider_rect, s_x, s_w = self.draw_audio_slider(mouse_pos)

            btn_easy = self.draw_button("EASY (TẬP SỰ)", 280, mouse_pos)
            btn_hard = self.draw_button("HARD (CAO THỦ)", 380, mouse_pos)
            btn_god  = self.draw_button("GOD (SIÊU AI)", 480, mouse_pos)
            btn_back = self.draw_button("<< QUAY LẠI", 650, mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                    
                # XỬ LÝ NHẤN CHUỘT XUỐNG
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_mute.collidepoint(mouse_pos):
                        am.toggle_mute(); am.play_sfx('ui')
                    elif slider_rect.collidepoint(mouse_pos):
                        self.dragging_vol = True
                        new_vol = (mouse_pos[0] - s_x) / s_w
                        am.set_volume(new_vol)
                    elif btn_easy.collidepoint(mouse_pos):
                        am.play_sfx('ui'); TetrisBotApp(difficulty="EASY").run(); self.screen = pygame.display.set_mode((self.screen_width, self.screen_height)); am.play_bgm(); return
                    elif btn_hard.collidepoint(mouse_pos):
                        am.play_sfx('ui'); TetrisBotApp(difficulty="HARD").run(); self.screen = pygame.display.set_mode((self.screen_width, self.screen_height)); am.play_bgm(); return
                    elif btn_god.collidepoint(mouse_pos):
                        am.play_sfx('ui'); TetrisBotApp(difficulty="GOD").run(); self.screen = pygame.display.set_mode((self.screen_width, self.screen_height)); am.play_bgm(); return
                    elif btn_back.collidepoint(mouse_pos):
                        am.play_sfx('ui'); return 
                
                # XỬ LÝ NHẢ CHUỘT RA
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.dragging_vol = False
                    
                # XỬ LÝ KÉO RÊ CHUỘT
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging_vol:
                        new_vol = (mouse_pos[0] - s_x) / s_w
                        am.set_volume(new_vol)

            pygame.display.flip()

    def run(self):
        """
        Khởi chạy vòng lặp Menu chính, đứng chờ sự tương tác của người chơi để vào các chế độ game khác nhau.
        """
        running = True
        self.dragging_vol = False
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            if am.ASSETS['bg']:
                bg_scaled = pygame.transform.smoothscale(am.ASSETS['bg'], (self.screen_width, self.screen_height))
                self.screen.blit(bg_scaled, (0, 0))
                overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150)); self.screen.blit(overlay, (0, 0))
            else:
                self.screen.fill((20, 20, 20))

            title_text = "TETRIS DSA"
            am.draw_text(self.screen, title_text, self.title_font, (0, 255, 255), 
                         (self.screen_width//2 - self.title_font.size(title_text)[0]//2, 140))
            
            author_text = "By: Duong Van Tai"
            am.draw_text(self.screen, author_text, self.btn_font, (200, 200, 200), 
                         (self.screen_width//2 - self.btn_font.size(author_text)[0]//2, 220))

            # VẼ VÀ LẤY VỊ TRÍ THANH TRƯỢT
            btn_mute, slider_rect, s_x, s_w = self.draw_audio_slider(mouse_pos)

            btn_single = self.draw_button("1 PLAYER MODE", 350, mouse_pos)
            btn_dual   = self.draw_button("2 PLAYER (PvP)", 450, mouse_pos)
            btn_bot    = self.draw_button("1 VS BOT (A.I)", 550, mouse_pos)
            btn_quit   = self.draw_button("QUIT GAME", 670, mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                    
                # XỬ LÝ NHẤN CHUỘT
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_mute.collidepoint(mouse_pos):
                        am.toggle_mute(); am.play_sfx('ui')
                    elif slider_rect.collidepoint(mouse_pos):
                        self.dragging_vol = True
                        new_vol = (mouse_pos[0] - s_x) / s_w
                        am.set_volume(new_vol)
                    elif btn_single.collidepoint(mouse_pos):
                        am.play_sfx('ui'); Game().run(); self.screen = pygame.display.set_mode((self.screen_width, self.screen_height)); am.play_bgm()
                    elif btn_dual.collidepoint(mouse_pos):
                        am.play_sfx('ui'); TetrisDualApp().run(); self.screen = pygame.display.set_mode((self.screen_width, self.screen_height)); am.play_bgm()
                    elif btn_bot.collidepoint(mouse_pos):
                        am.play_sfx('ui'); self.run_bot_menu()
                    elif btn_quit.collidepoint(mouse_pos):
                        am.play_sfx('ui'); pygame.quit(); sys.exit()
                
                # XỬ LÝ NHẢ CHUỘT
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.dragging_vol = False
                    
                # XỬ LÝ KÉO RÊ CHUỘT TRÊN THANH TRƯỢT
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging_vol:
                        new_vol = (mouse_pos[0] - s_x) / s_w
                        am.set_volume(new_vol)

            pygame.display.flip()

if __name__ == "__main__":
    MainMenu().run()