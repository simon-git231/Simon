import pygame
import sys
import random
from collections import deque
from pygame.locals import *

# =========================
# BASIC CONFIG
# =========================

UNLOCK_PASSWORD = "4657"

pygame.init()
pygame.font.init()

FONT = pygame.font.SysFont("consolas", 22)
BIG_FONT = pygame.font.SysFont("consolas", 40)

SCREEN = pygame.display.set_mode((0, 0), FULLSCREEN)
W, H = SCREEN.get_size()
CLOCK = pygame.time.Clock()

WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE = (50,150,255)
GREEN = (50,200,100)
RED = (220,50,50)
YELLOW = (240,220,60)

state = {
    "first_name": "",
    "last_name": "",
    "screen": "setup",   # setup, startmenu, pacman, snake, breaker, terminal, locked
    "locked": False
}

# =========================
# UI HELPERS
# =========================

def draw_text(text, x, y, font=FONT, color=WHITE):
    SCREEN.blit(font.render(text, True, color), (x,y))

def button(rect, text):
    pygame.draw.rect(SCREEN, BLUE, rect)
    draw_text(text, rect[0] + 10, rect[1] + 10, BIG_FONT)

def input_box(prompt):
    text = ""
    cursor = True
    timer = 0

    while True:
        for ev in pygame.event.get():
            if ev.type == KEYDOWN:
                if ev.key == K_RETURN:
                    return text
                elif ev.key == K_BACKSPACE:
                    text = text[:-1]
                else:
                    if ev.unicode:
                        text += ev.unicode
            elif ev.type == QUIT:
                # ignore window close; only exit via terminal
                pass

        SCREEN.fill(BLACK)
        draw_text(prompt, W//2 - 250, H//2 - 60, BIG_FONT)
        pygame.draw.rect(SCREEN, WHITE, (W//2 - 250, H//2, 500, 50), 2)
        draw_text(text, W//2 - 240, H//2 + 5, BIG_FONT)

        timer += CLOCK.get_time()
        if timer > 500:
            cursor = not cursor
            timer = 0

        if cursor:
            draw_text("_", W//2 - 240 + FONT.size(text)[0], H//2 + 5, BIG_FONT)

        pygame.display.flip()
        CLOCK.tick(30)

# =========================
# GAMES
# =========================

def run_snake():
    grid = 20
    cols = W // grid
    rows = H // grid
    snake = deque([(cols//2, rows//2)])
    dirx, diry = 1, 0
    food = (random.randint(1, cols-2), random.randint(1, rows-2))

    while True:
        for ev in pygame.event.get():
            if ev.type == KEYDOWN:
                if ev.key == K_ESCAPE:
                    return
                if ev.key == K_UP: dirx, diry = 0,-1
                if ev.key == K_DOWN: dirx, diry = 0,1
                if ev.key == K_LEFT: dirx, diry = -1,0
                if ev.key == K_RIGHT: dirx, diry = 1,0
            elif ev.type == QUIT:
                pass

        head = snake[0]
        new = ((head[0]+dirx)%cols, (head[1]+diry)%rows)

        if new in snake:
            return

        snake.appendleft(new)
        if new == food:
            food = (random.randint(1, cols-2), random.randint(1, rows-2))
        else:
            snake.pop()

        SCREEN.fill(BLACK)
        for x,y in snake:
            pygame.draw.rect(SCREEN, GREEN, (x*grid, y*grid, grid-1, grid-1))
        pygame.draw.rect(SCREEN, RED, (food[0]*grid, food[1]*grid, grid-1, grid-1))
        draw_text("Snake - ESC to return", 10, 10)
        pygame.display.flip()
        CLOCK.tick(10)

def run_breaker():
    # Make bricks cover the full width
    rows = 5
    cols = 12  # more columns to fill the row
    top_margin = 80
    side_margin = 10
    brick_gap = 4

    brick_w = (W - 2*side_margin - (cols-1)*brick_gap) // cols
    brick_h = 30

    paddle_w = max(120, W // 8)
    paddle_x = W//2 - paddle_w//2
    paddle_y = H - 60
    ball_x, ball_y = W//2, H//2
    ball_vx, ball_vy = 5, -5

    bricks = []
    for r in range(rows):
        for c in range(cols):
            x = side_margin + c*(brick_w + brick_gap)
            y = top_margin + r*(brick_h + brick_gap)
            bricks.append(pygame.Rect(x, y, brick_w, brick_h))

    while True:
        for ev in pygame.event.get():
            if ev.type == KEYDOWN and ev.key == K_ESCAPE:
                return
            elif ev.type == QUIT:
                pass

        keys = pygame.key.get_pressed()
        if keys[K_LEFT]: paddle_x -= 10
        if keys[K_RIGHT]: paddle_x += 10
        paddle_x = max(0, min(W-paddle_w, paddle_x))

        ball_x += ball_vx
        ball_y += ball_vy

        if ball_x <= 0 or ball_x >= W: ball_vx *= -1
        if ball_y <= 0: ball_vy *= -1
        if ball_y > H: return

        paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_w, 20)
        ball_rect = pygame.Rect(ball_x-8, ball_y-8, 16, 16)

        if ball_rect.colliderect(paddle_rect):
            ball_vy = -abs(ball_vy)

        hit_index = None
        for i,b in enumerate(bricks):
            if ball_rect.colliderect(b):
                hit_index = i
                break
        if hit_index is not None:
            del bricks[hit_index]
            ball_vy *= -1

        SCREEN.fill(BLACK)
        pygame.draw.rect(SCREEN, WHITE, paddle_rect)
        pygame.draw.circle(SCREEN, YELLOW, (ball_x, ball_y), 8)
        for b in bricks:
            pygame.draw.rect(SCREEN, BLUE, b)
        draw_text("Block Breaker - ESC to return", 10, 10)
        pygame.display.flip()
        CLOCK.tick(60)

def run_pacman():
    grid = 24
    cols = W // grid
    rows = H // grid
    pac = [cols//2, rows//2]
    dirx, diry = 0,0
    dots = {(x,y) for x in range(cols) for y in range(rows)}

    while True:
        for ev in pygame.event.get():
            if ev.type == KEYDOWN:
                if ev.key == K_ESCAPE: return
                if ev.key == K_UP: dirx, diry = 0,-1
                if ev.key == K_DOWN: dirx, diry = 0,1
                if ev.key == K_LEFT: dirx, diry = -1,0
                if ev.key == K_RIGHT: dirx, diry = 1,0
            elif ev.type == QUIT:
                pass

        pac[0] = (pac[0]+dirx)%cols
        pac[1] = (pac[1]+diry)%rows
        dots.discard((pac[0], pac[1]))

        SCREEN.fill(BLACK)
        for x,y in list(dots)[:2000]:
            pygame.draw.circle(SCREEN, WHITE, (x*grid+12, y*grid+12), 3)
        pygame.draw.circle(SCREEN, YELLOW, (pac[0]*grid+12, pac[1]*grid+12), 10)
        draw_text("Pacman - ESC to return", 10, 10)
        pygame.display.flip()
        CLOCK.tick(10)

# =========================
# TERMINAL
# =========================

def run_terminal():
    history = []
    text = ""
    cursor = True
    timer = 0

    while True:
        for ev in pygame.event.get():
            if ev.type == KEYDOWN:
                if ev.key == K_ESCAPE:
                    return
                elif ev.key == K_BACKSPACE:
                    text = text[:-1]
                elif ev.key == K_RETURN:
                    cmd = text.strip()
                    history.append("> " + cmd)
                    if process_terminal(cmd, history):
                        pygame.quit()
                        sys.exit()
                    text = ""
                else:
                    if ev.unicode:
                        text += ev.unicode
            elif ev.type == QUIT:
                pass

        SCREEN.fill(BLACK)
        y = 20
        for line in history[-20:]:
            draw_text(line, 10, y)
            y += 28

        draw_text("> " + text + ("_" if cursor else ""), 10, H-50)

        timer += CLOCK.get_time()
        if timer > 500:
            cursor = not cursor
            timer = 0

        pygame.display.flip()
        CLOCK.tick(30)

def process_terminal(cmd, history):
    cmd = cmd.lower()

    if cmd.startswith("echo "):
        history.append(cmd[5:])
        return False

    if cmd == "lock activeos":
        history.append("[system] activeOS locked.")
        state["locked"] = True
        state["screen"] = "locked"
        return False

    if cmd == "exit activeos":
        history.append("[system] Shutting down...")
        return True

    if cmd == "help":
        history.append("Commands: echo <text>, lock activeOS, exit activeOS")
        return False

    history.append("Unknown command")
    return False

# =========================
# LOCK SCREEN
# =========================

def run_locked_screen():
    entering = False
    password = ""

    while state["locked"]:
        for ev in pygame.event.get():
            if ev.type == KEYDOWN:
                mods = pygame.key.get_mods()

                if (mods & KMOD_CTRL) and (mods & KMOD_SHIFT) and ev.key in (K_3, K_KP3):
                    entering = True
                    password = ""

                elif entering:
                    if ev.key == K_RETURN:
                        if password == UNLOCK_PASSWORD:
                            state["locked"] = False
                            state["screen"] = "startmenu"
                            return
                        entering = False
                        password = ""
                    elif ev.key == K_BACKSPACE:
                        password = password[:-1]
                    else:
                        if ev.unicode:
                            password += ev.unicode
            elif ev.type == QUIT:
                pass

        SCREEN.fill((10,10,30))
        draw_text("activeOS is locked.", W//2 - 200, H//2 - 80, BIG_FONT)
        draw_text("Press Ctrl + Shift + 3 to unlock.", W//2 - 260, H//2 - 20)

        if entering:
            draw_text("Password: " + "*"*len(password),
                      W//2 - 200, H//2 + 40, BIG_FONT, YELLOW)

        pygame.display.flip()
        CLOCK.tick(30)

# =========================
# START MENU
# =========================

def run_startmenu():
    btn_w, btn_h = 300, 70
    x = W//2 - btn_w//2
    y = H//2 - 200

    buttons = [
        ("Pacman", "pacman"),
        ("Snake", "snake"),
        ("Block Breaker", "breaker"),
        ("Terminal", "terminal")
    ]

    while True:
        for ev in pygame.event.get():
            if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                mx,my = ev.pos
                for i,(_,scr) in enumerate(buttons):
                    rect = pygame.Rect(x, y + i*90, btn_w, btn_h)
                    if rect.collidepoint(mx,my):
                        state["screen"] = scr
                        return
            elif ev.type == QUIT:
                pass

        SCREEN.fill((18,18,40))
        draw_text(f"activeOS - Welcome {state['first_name']}", 20, 20, BIG_FONT)

        for i,(label,_) in enumerate(buttons):
            rect = pygame.Rect(x, y + i*90, btn_w, btn_h)
            button(rect, label)

        draw_text("To exit: open Terminal and type 'exit activeOS'",
                  20, H - 40)

        pygame.display.flip()
        CLOCK.tick(30)

# =========================
# SETUP
# =========================

def run_setup():
    SCREEN.fill(BLACK)
    draw_text("Welcome to activeOS Setup", W//2 - 250, H//2 - 120, BIG_FONT)
    pygame.display.flip()
    pygame.time.delay(400)

    first = input_box("Enter your first name:")
    last = input_box("Enter your last name:")

    state["first_name"] = first or ""
    state["last_name"] = last or ""
    state["screen"] = "startmenu"

# =========================
# MAIN LOOP
# =========================

def main_loop():
    while True:
        if state["screen"] == "setup":
            run_setup()

        elif state["locked"]:
            run_locked_screen()

        elif state["screen"] == "startmenu":
            run_startmenu()

        elif state["screen"] == "snake":
            run_snake()
            state["screen"] = "startmenu"

        elif state["screen"] == "breaker":
            run_breaker()
            state["screen"] = "startmenu"

        elif state["screen"] == "pacman":
            run_pacman()
            state["screen"] = "startmenu"

        elif state["screen"] == "terminal":
            run_terminal()
            state["screen"] = "startmenu"

        else:
            state["screen"] = "startmenu"

        for ev in pygame.event.get():
            if ev.type == QUIT:
                pass

        CLOCK.tick(30)

# =========================
# ENTRY POINT
# =========================

if __name__ == "__main__":
    main_loop()
