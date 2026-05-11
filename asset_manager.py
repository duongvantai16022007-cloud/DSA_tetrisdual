"""
Mô đun: asset_manager.py
Mô tả: Quản lý tập trung toàn bộ tài nguyên (assets) của game bao gồm hình ảnh, âm thanh, và font chữ.
Cung cấp các hàm tiện ích để tải, phát âm thanh, vẽ chữ và quản lý trạng thái âm lượng.
"""
import pygame
import os
import random

_initialized = False
ASSETS = {
    'bg': None,
    'blocks': {},
    'bg_list': [],
    'bgm_list': [],
    'sfx': {},
    'ui': {}, # Thêm dict quản lý ảnh UI
    'font_path': None
}
CELL_SIZE = 30
COLORS = {
    'I': (0, 255, 255), 'J': (0, 0, 255), 'L': (255, 165, 0),
    'O': (255, 255, 0), 'S': (0, 255, 0), 'T': (128, 0, 128), 'Z': (255, 0, 0)
}

global_vol = 0.3
is_muted = False

def init_assets():
    """
    Khởi tạo và tải toàn bộ tài nguyên từ thư mục 'asset' vào bộ nhớ (từ điển ASSETS).
    Chỉ thực hiện một lần duy nhất khi game bắt đầu.
    """
    global _initialized
    if _initialized: return
    
    try: pygame.mixer.init()
    except Exception: pass 
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.join(base_dir, 'asset')
    tile_paths = {}
    
    if os.path.exists(asset_dir):
        for root, dirs, files in os.walk(asset_dir):
            for file in files:
                ext = file.lower().split('.')[-1]
                path = os.path.join(root, file)
                
                if file == 'Heart Bubble.otf': ASSETS['font_path'] = path
                elif file == 'boom.wav': 
                    try: ASSETS['sfx']['clear'] = pygame.mixer.Sound(path)
                    except: pass
                elif file == 'ui.wav': 
                    try: ASSETS['sfx']['ui'] = pygame.mixer.Sound(path)
                    except: pass
                elif file == 'win.mp3': 
                    try: ASSETS['sfx']['win'] = pygame.mixer.Sound(path)
                    except: pass
                elif ext == 'mp3' and file != 'win.mp3': 
                    ASSETS['bgm_list'].append(path)
                    
                elif ext in ['jpg', 'jpeg']:
                    ASSETS['bg_list'].append(path)
                elif ext == 'png':
                    # Load file icon âm nhạc
                    if file == 'emote_music.png':
                        try:
                            img = pygame.image.load(path)
                            if pygame.display.get_surface(): img = img.convert_alpha()
                            ASSETS['ui']['music'] = pygame.transform.scale(img, (35, 35))
                        except Exception: pass
                    elif file.startswith('tile_000'):
                        tile_paths[file] = path
                    elif 'background' in root.lower() or 'bg' in root.lower():
                        ASSETS['bg_list'].append(path)

    shapes = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
    for i, shape in enumerate(shapes):
        t_name = f'tile_{i:04d}.png'
        if t_name in tile_paths:
            try:
                img = pygame.image.load(tile_paths[t_name])
                if pygame.display.get_surface(): img = img.convert_alpha()
                ASSETS['blocks'][shape] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
            except Exception: _create_fallback_block(shape)
        else: _create_fallback_block(shape)
            
    change_background()
    _initialized = True

def _create_fallback_block(shape):
    """
    Tạo một khối hình vuông đồ họa cơ bản trong trường hợp không tìm thấy file ảnh asset.
    
    Args:
        shape (str): Tên của loại khối ('I', 'J', 'L', 'O', 'S', 'T', 'Z').
    """
    surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
    surf.fill(COLORS.get(shape, (255, 255, 255)))
    pygame.draw.rect(surf, (200, 200, 200), surf.get_rect(), 1)
    ASSETS['blocks'][shape] = surf

def change_background():
    """
    Thay đổi hình nền của game bằng cách chọn ngẫu nhiên một hình ảnh từ danh sách `bg_list`.
    """
    if ASSETS['bg_list']:
        chosen = random.choice(ASSETS['bg_list'])
        try: 
            img = pygame.image.load(chosen)
            if pygame.display.get_surface(): img = img.convert()
            ASSETS['bg'] = img
        except Exception: ASSETS['bg'] = None

def get_font(size, bold=False):
    """
    Tạo và trả về đối tượng font chữ của Pygame. 
    Ưu tiên font tùy chỉnh nếu có, ngược lại dùng font hệ thống.
    
    Args:
        size (int): Kích thước font chữ.
        bold (bool, optional): In đậm (chỉ áp dụng cho font hệ thống). Mặc định là False.
        
    Returns:
        pygame.font.Font: Đối tượng font chữ.
    """
    if ASSETS['font_path']:
        try: return pygame.font.Font(ASSETS['font_path'], size)
        except Exception: pass
    return pygame.font.SysFont('Consolas', size, bold=bold)

def toggle_mute():
    """
    Bật hoặc tắt trạng thái tắt tiếng (mute) cho toàn bộ game.
    
    Returns:
        bool: Trạng thái mute hiện tại (True nếu đang tắt tiếng, False nếu đang mở).
    """
    global is_muted
    is_muted = not is_muted
    if pygame.mixer.get_init():
        if is_muted: pygame.mixer.music.set_volume(0)
        else: pygame.mixer.music.set_volume(global_vol)
    return is_muted

def set_volume(vol):
    """
    Cập nhật mức âm lượng toàn cục (thường dùng cho thanh trượt kéo/thả trên UI).
    
    Args:
        vol (float): Giá trị âm lượng từ 0.0 đến 1.0.
    """
    global global_vol, is_muted
    global_vol = max(0.0, min(1.0, vol))
    if global_vol == 0:
        is_muted = True
    else:
        is_muted = False
        
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(0 if is_muted else global_vol)

def play_sfx(name):
    """
    Phát một hiệu ứng âm thanh (Sound Effect) nếu không bị tắt tiếng.
    
    Args:
        name (str): Tên của hiệu ứng âm thanh cần phát (VD: 'clear', 'ui', 'win').
    """
    if name in ASSETS['sfx'] and not is_muted:
        try: 
            sfx_vol = min(1.0, global_vol + 0.3)
            ASSETS['sfx'][name].set_volume(sfx_vol)
            ASSETS['sfx'][name].play()
        except: pass

def play_bgm():
    """
    Phát nhạc nền ngẫu nhiên từ danh sách BGM được nạp vào bộ nhớ. Phát lặp lại vô hạn.
    """
    if ASSETS['bgm_list'] and pygame.mixer.get_init():
        try:
            pygame.mixer.music.load(random.choice(ASSETS['bgm_list']))
            pygame.mixer.music.set_volume(0 if is_muted else global_vol)
            pygame.mixer.music.play(-1)
        except Exception: pass

def stop_bgm():
    """
    Dừng phát nhạc nền hiện tại.
    """
    if pygame.mixer.get_init(): pygame.mixer.music.stop()

def draw_text(surface, text, font, color, pos, shadow_color=(0,0,0)):
    """
    Vẽ văn bản có đổ bóng lên một bề mặt (surface) để chữ dễ đọc hơn trên nền phức tạp.
    
    Args:
        surface (pygame.Surface): Bề mặt đích để vẽ lên (thường là màn hình).
        text (str): Nội dung văn bản.
        font (pygame.font.Font): Đối tượng font chữ.
        color (tuple): Màu sắc của chữ (R, G, B).
        pos (tuple): Vị trí (x, y) để vẽ văn bản.
        shadow_color (tuple, optional): Màu đổ bóng. Mặc định là đen (0,0,0).
    """
    shadow_surf = font.render(text, True, shadow_color)
    text_surf = font.render(text, True, color)
    surface.blit(shadow_surf, (pos[0]+2, pos[1]+2))
    surface.blit(text_surf, pos)