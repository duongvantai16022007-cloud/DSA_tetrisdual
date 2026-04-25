import pygame
import sys
from main import Game
from dualmode import TetrisDualApp

class MainMenu():
    def __init__(self):
        pygame.init()
        self.screen_width = 600
        self.screen_height = 700
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("UIT Tetris - Main Menu")
        
        self.title_font = pygame.font.SysFont('Consolas', 60, bold=True)
        self.btn_font = pygame.font.SysFont('Consolas', 30, bold=True)

    def draw_button(self, text, y_pos, mouse_pos):
        btn_width = 400
        btn_height = 70
        btn_x = (self.screen_width - btn_width) // 2
        btn_rect = pygame.Rect(btn_x, y_pos, btn_width, btn_height)

        if btn_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, (100, 100, 100), btn_rect)  
        else:
            pygame.draw.rect(self.screen, (40, 40, 40), btn_rect)     

        pygame.draw.rect(self.screen, (255, 255, 255), btn_rect, 2)

        text_surf = self.btn_font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=btn_rect.center)
        self.screen.blit(text_surf, text_rect)

        return btn_rect

    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            self.screen.fill((20, 20, 20))

            title_text = self.title_font.render("TETRIS DSA", True, (0, 255, 255))
            title_rect = title_text.get_rect(center=(self.screen_width // 2, 150))
            self.screen.blit(title_text, title_rect)
            
            author_text = self.btn_font.render("By: Duong Van Tai", True, (200, 200, 200))
            author_rect = author_text.get_rect(center=(self.screen_width // 2, 220))
            self.screen.blit(author_text, author_rect)

            btn_single = self.draw_button("1 PLAYER MODE", 350, mouse_pos)
            btn_dual = self.draw_button("2 PLAYER (PvP)", 450, mouse_pos)
            btn_quit = self.draw_button("QUIT GAME", 550, mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_single.collidepoint(mouse_pos):
                        game1 = Game()
                        game1.run()
                        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
                    
                    elif btn_dual.collidepoint(mouse_pos):
                        game2 = TetrisDualApp()
                        game2.run()
                        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
                    
                    elif btn_quit.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

            pygame.display.flip()

if __name__ == "__main__":
    menu = MainMenu()
    menu.run()