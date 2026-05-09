"""
Snake Game — Python avec Pygame
================================
Installation : pip install pygame
Lancement    : python snake.py

Contrôles
---------
  ↑ ↓ ← →  ou  W A S D  — diriger le serpent
  P             — pause
  R             — rejouer après game over
  Échap         — quitter
"""

import pygame
import random
import sys


COLS, ROWS = 20, 20
CELL       = 28
WIDTH      = COLS * CELL          # 560
HEIGHT     = ROWS * CELL + 80     # 640  (80px pour le HUD)
FPS        = 60


C_BG       = (13,  17,  23)
C_GRID_A   = (17,  24,  39)
C_GRID_B   = (15,  23,  42)
C_HEAD     = (74, 222, 128)
C_BODY     = (22, 163,  74)
C_BODY2    = (22, 101,  52)
C_APPLE    = (248, 113, 113)
C_SHINE    = (252, 165, 165)
C_STEM     = (185,  28,  28)
C_EYE      = (13,  17,  23)
C_TEXT     = (255, 255, 255)
C_MUTED    = (107, 114, 128)
C_GREEN    = (74, 222, 128)
C_RED      = (248, 113, 113)

SPEED_BASE = 8    # cases/seconde au niveau 1
SPEED_STEP = 1    # +1 case/s tous les 5 pts



def rnd_cell():
    return (random.randrange(COLS), random.randrange(ROWS))

def draw_rounded_rect(surf, color, rect, radius=6):
    pygame.draw.rect(surf, color, rect, border_radius=radius)

def draw_text(surf, text, size, color, cx, cy, bold=False):
    font = pygame.font.SysFont("Courier New", size, bold=bold)
    img  = font.render(text, True, color)
    r    = img.get_rect(center=(cx, cy))
    surf.blit(img, r)



class Apple:
    def __init__(self, snake_cells):
        self.pos = self._spawn(snake_cells)

    def _spawn(self, occupied):
        while True:
            p = rnd_cell()
            if p not in occupied:
                return p

    def draw(self, surf):
        x, y = self.pos[0] * CELL + CELL // 2, self.pos[1] * CELL + CELL // 2
        r = CELL // 2 - 4
        pygame.draw.circle(surf, C_APPLE, (x, y), r)
        pygame.draw.circle(surf, C_SHINE, (x - 3, y - 3), max(3, r // 3))
        pygame.draw.line(surf, C_STEM, (x, y - r), (x + 4, y - r - 4), 2)


class Snake:
    def __init__(self):
        self.body  = [(10, 10), (9, 10), (8, 10)]
        self.dir   = (1, 0)
        self.next  = (1, 0)
        self.alive = True

    def set_dir(self, dx, dy):
        if (dx, dy) == (-self.dir[0], -self.dir[1]):
            return   # demi-tour interdit
        self.next = (dx, dy)

    def update(self, apple_pos):
        """Avance d'une case. Retourne True si pomme mangée."""
        self.dir = self.next
        head = (self.body[0][0] + self.dir[0],
                self.body[0][1] + self.dir[1])

        if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS):
            self.alive = False
            return False

        if head in self.body:
            self.alive = False
            return False

        self.body.insert(0, head)
        if head == apple_pos:
            return True   # pomme mangée → queue conservée
        else:
            self.body.pop()
            return False

    def draw(self, surf):
        for i, (cx, cy) in enumerate(self.body):
            rx, ry = cx * CELL + 2, cy * CELL + 2
            rw, rh = CELL - 4, CELL - 4
            color  = C_HEAD if i == 0 else (C_BODY if i % 2 == 0 else C_BODY2)
            radius = 8 if i == 0 else 4
            draw_rounded_rect(surf, color, pygame.Rect(rx, ry, rw, rh), radius)

            if i == 0:
                hx, hy = cx * CELL, cy * CELL
                dx, dy = self.dir
                if   dx ==  1: eyes = [(hx+18, hy+6),  (hx+18, hy+16)]
                elif dx == -1: eyes = [(hx+6,  hy+6),  (hx+6,  hy+16)]
                elif dy ==  1: eyes = [(hx+6,  hy+18), (hx+16, hy+18)]
                else:          eyes = [(hx+6,  hy+6),  (hx+16, hy+6)]
                for ex, ey in eyes:
                    pygame.draw.circle(surf, C_EYE, (ex, ey), 3)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock  = pygame.time.Clock()
        self.best   = 0
        self.reset()

    def reset(self):
        self.snake    = Snake()
        self.apple    = Apple(set(self.snake.body))
        self.score    = 0
        self.level    = 1
        self.paused   = False
        self.over     = False
        self.tick_acc = 0.0

    def step_interval(self):
        speed = SPEED_BASE + (self.level - 1) * SPEED_STEP
        return 1.0 / speed

    # ── Dessin ─
    def draw_grid(self):
        for x in range(COLS):
            for y in range(ROWS):
                color = C_GRID_A if (x + y) % 2 == 0 else C_GRID_B
                self.screen.fill(color, (x * CELL, y * CELL, CELL, CELL))

    def draw_hud(self):
        hud_y = ROWS * CELL
        self.screen.fill(C_BG, (0, hud_y, WIDTH, 80))
        third = WIDTH // 3
        items = [
            ("SCORE",  str(self.score), C_TEXT),
            ("RECORD", str(self.best),  C_GREEN),
            ("NIVEAU", str(self.level), C_TEXT),
        ]
        for i, (label, value, col) in enumerate(items):
            cx = third * i + third // 2
            draw_text(self.screen, label, 11, C_MUTED, cx, hud_y + 20)
            draw_text(self.screen, value, 26, col,     cx, hud_y + 54, bold=True)

    def draw_overlay(self, title, title_color, subtitle="", score_big=None):
        overlay = pygame.Surface((WIDTH, ROWS * CELL), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        self.screen.blit(overlay, (0, 0))
        mid_x, mid_y = WIDTH // 2, ROWS * CELL // 2
        draw_text(self.screen, title, 34, title_color, mid_x, mid_y - 60, bold=True)
        if score_big is not None:
            draw_text(self.screen, str(score_big), 56, C_GREEN,  mid_x, mid_y)
            draw_text(self.screen, f"Record : {self.best}", 16, C_MUTED, mid_x, mid_y + 50)
            draw_text(self.screen, "R — Rejouer    Echap — Quitter", 14, C_MUTED, mid_x, mid_y + 90)
        else:
            draw_text(self.screen, subtitle, 17, C_MUTED, mid_x, mid_y - 10)
            draw_text(self.screen, "Appuyez sur ENTREE pour jouer", 15, C_MUTED, mid_x, mid_y + 50)

    
    def run(self):
        show_start = True

        while True:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    k = event.key

                    if show_start and k == pygame.K_RETURN:
                        show_start = False

                    elif self.over:
                        if k == pygame.K_r:      self.reset()
                        if k == pygame.K_ESCAPE: pygame.quit(); sys.exit()

                    else:
                        if k == pygame.K_p:
                            self.paused = not self.paused

                        dirs = {
                            pygame.K_UP:    (0, -1), pygame.K_w: (0, -1),
                            pygame.K_DOWN:  (0,  1), pygame.K_s: (0,  1),
                            pygame.K_LEFT:  (-1, 0), pygame.K_a: (-1, 0),
                            pygame.K_RIGHT: (1,  0), pygame.K_d: (1,  0),
                        }
                        if k in dirs and not self.paused:
                            self.snake.set_dir(*dirs[k])

                        if k == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()

            # Mise à jour logique
            if not show_start and not self.over and not self.paused:
                self.tick_acc += dt
                if self.tick_acc >= self.step_interval():
                    self.tick_acc = 0.0
                    ate = self.snake.update(self.apple.pos)
                    if ate:
                        self.score += 1
                        if self.score > self.best:
                            self.best = self.score
                        self.level = self.score // 5 + 1
                        self.apple = Apple(set(self.snake.body))
                    if not self.snake.alive:
                        self.over = True

            # Dessin
            self.screen.fill(C_BG)
            self.draw_grid()
            self.apple.draw(self.screen)
            self.snake.draw(self.screen)
            self.draw_hud()

            if show_start:
                self.draw_overlay("SNAKE", C_GREEN,
                                  subtitle="Mangez les pommes, evitez les murs !")
            elif self.over:
                self.draw_overlay("GAME OVER", C_RED, score_big=self.score)
            elif self.paused:
                self.draw_overlay("PAUSE", C_TEXT, subtitle="P — continuer")

            pygame.display.flip()


# ── Lancement 
if __name__ == "__main__":
    Game().run()