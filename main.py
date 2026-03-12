import pygame
import sys
import os
from maps import LEVELS, LEVEL_META, load_level
from sokoban import Sokoban

pygame.init()

WINDOW_WIDTH  = 900
WINDOW_HEIGHT = 650
FPS           = 60

FONT_BIG   = pygame.font.SysFont("arial", 32)
FONT_MED   = pygame.font.SysFont("arial", 20)
FONT_SMALL = pygame.font.SysFont("arial", 15)

COL_BG      = (28,  28,  35)
COL_PANEL   = (18,  18,  24)
COL_WHITE   = (230, 230, 230)
COL_GREY    = (110, 110, 120)
COL_ACCENT  = (0,   190, 220)
COL_GREEN   = (80,  200,  80)
COL_EASY    = (70,  170, 100)
COL_MEDIUM  = (200, 160,  40)
COL_HARD    = (200,  70,  70)
COL_BTN     = (45,   55,  75)
COL_BTN_HOV = (65,   85, 115)

MAX_TILE    = 64
HUD_HEIGHT  = 48

DIFF_COLOURS = {"EASY": COL_EASY, "MEDIUM": COL_MEDIUM, "HARD": COL_HARD}

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


# ── Assets ──────────────────────────────────────────────────────────────────

def make_fallback(col, size):
    s = pygame.Surface((size, size))
    s.fill(col)
    return s

def load_img(name, size):
    try:
        img = pygame.image.load(os.path.join(ASSETS_DIR, name))
        return pygame.transform.scale(img, (size, size))
    except Exception:
        fb = {"wall.png":(80,80,80),"floor.png":(45,45,45),"box.png":(180,120,40),
              "goal.png":(40,160,40),"player.png":(60,120,220),
              "box_on_goal.png":(220,180,40),"player_on_goal.png":(60,180,220)}
        return make_fallback(fb.get(name,(200,0,200)), size)

def load_assets(ts):
    return {k: load_img(v, ts) for k, v in {
        "wall":"wall.png","floor":"floor.png","goal":"goal.png",
        "box":"box.png","box_on_goal":"box_on_goal.png",
        "player":"player.png","player_on_goal":"player_on_goal.png"
    }.items()}


# ── Rendering ────────────────────────────────────────────────────────────────

def tile_size(game):
    ts = min(WINDOW_WIDTH // game.width, (WINDOW_HEIGHT - HUD_HEIGHT) // game.height, MAX_TILE)
    return max(ts, 8)

def draw_grid(screen, game, assets, ts):
    ox = (WINDOW_WIDTH  - game.width  * ts) // 2
    oy = (WINDOW_HEIGHT - HUD_HEIGHT - game.height * ts) // 2
    for y, row in enumerate(game.level):
        for x, tile in enumerate(row):
            px, py = ox + x*ts, oy + y*ts
            # Always draw floor first, then overlay
            screen.blit(assets["floor"], (px, py))
            if   tile == '#':
                screen.blit(assets["wall"], (px, py))
            elif tile == '.':
                screen.blit(assets["goal"], (px, py))
            elif tile == '$':
                screen.blit(assets["box"], (px, py))
            elif tile == '*':
                screen.blit(assets["goal"], (px, py))
                screen.blit(assets["box_on_goal"], (px, py))
            elif tile == '@':
                screen.blit(assets["player"], (px, py))
            elif tile == '+':
                screen.blit(assets["goal"], (px, py))
                screen.blit(assets["player_on_goal"], (px, py))

def draw_hud(screen, game, idx):
    pygame.draw.rect(screen, COL_PANEL, (0, WINDOW_HEIGHT-HUD_HEIGHT, WINDOW_WIDTH, HUD_HEIGHT))
    pygame.draw.line(screen, (50,50,60), (0, WINDOW_HEIGHT-HUD_HEIGHT), (WINDOW_WIDTH, WINDOW_HEIGHT-HUD_HEIGHT))
    name, diff = LEVEL_META[idx]
    items = [
        (f"{idx+1}. {name}", DIFF_COLOURS[diff]),
        (f"Moves: {game.move_count}", COL_WHITE),
        (f"Pushes: {game.push_count}", COL_WHITE),
        (f"Left: {game.count_remaining_boxes()}", COL_GREY),
        ("↑↓←→  R=Reset  Z=Undo  ESC=Menu", COL_GREY),
    ]
    x = 16
    cy = WINDOW_HEIGHT - HUD_HEIGHT//2
    for text, col in items:
        s = FONT_SMALL.render(text, True, col)
        screen.blit(s, (x, cy - s.get_height()//2))
        x += s.get_width() + 28

def draw_menu(screen, scroll, hover):
    screen.fill(COL_BG)
    t = FONT_BIG.render("SOKOBAN", True, COL_ACCENT)
    screen.blit(t, ((WINDOW_WIDTH - t.get_width())//2, 28))

    cols, bw, bh, gap = 4, 190, 46, 12
    tw = cols*bw + (cols-1)*gap
    sx = (WINDOW_WIDTH - tw)//2
    clip = pygame.Rect(0, 90, WINDOW_WIDTH, WINDOW_HEIGHT-90)
    screen.set_clip(clip)

    last_diff = None
    row_count = 0
    for i, (name, diff) in enumerate(LEVEL_META):
        if diff != last_diff:
            last_diff = diff
            row_count = 0
        col_idx = row_count % cols
        row_idx  = row_count // cols
        # group offset by difficulty
        group_y = {"EASY":0,"MEDIUM":3,"HARD":7}[diff] * (bh+gap)
        y = 100 + group_y + (row_idx*(bh+gap)) - scroll
        x = sx + col_idx * (bw+gap)
        row_count += 1

        rect = pygame.Rect(x, y, bw, bh)
        if not clip.colliderect(rect):
            continue

        dcol = DIFF_COLOURS[diff]
        bg = COL_BTN_HOV if i==hover else COL_BTN
        pygame.draw.rect(screen, bg, rect, border_radius=5)
        pygame.draw.rect(screen, dcol, rect, 2, border_radius=5)

        lbl = FONT_SMALL.render(f"{i+1}. {name}", True, COL_WHITE)
        dlbl = FONT_SMALL.render(diff, True, dcol)
        screen.blit(lbl, (x+8, y+4))
        screen.blit(dlbl, (x+8, y+bh-dlbl.get_height()-4))

    screen.set_clip(None)

    # Difficulty legend
    lx = 24
    for label, col in [("■ EASY","EASY"),("■ MEDIUM","MEDIUM"),("■ HARD","HARD")]:
        s = FONT_SMALL.render(label, True, DIFF_COLOURS[col])
        screen.blit(s, (lx, WINDOW_HEIGHT-28))
        lx += s.get_width() + 20

def draw_complete(screen, game, idx):
    screen.fill((10,10,15))
    name, diff = LEVEL_META[idx]
    for text, col, dy in [
        ("✓  LEVEL COMPLETE!",                              COL_GREEN,  -70),
        (f"{name}  [{diff}]",                               DIFF_COLOURS[diff], -20),
        (f"Moves: {game.move_count}   Pushes: {game.push_count}", COL_WHITE, 30),
        ("ENTER = Menu     R = Replay",                     COL_GREY,   80),
    ]:
        s = FONT_BIG.render(text, True, col)
        screen.blit(s, ((WINDOW_WIDTH-s.get_width())//2, WINDOW_HEIGHT//2 + dy))


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Sokoban")
    clock  = pygame.time.Clock()

    state   = "menu"
    sel     = 0
    game    = None
    assets  = {}
    scroll  = 0
    hover   = -1

    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if state == "menu":
                if ev.type == pygame.MOUSEWHEEL:
                    scroll = max(0, scroll - ev.y*28)
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    cols, bw, bh, gap = 4, 190, 46, 12
                    tw = cols*bw + (cols-1)*gap
                    sx = (WINDOW_WIDTH-tw)//2
                    row_count = 0; last_diff = None
                    for i, (name, diff) in enumerate(LEVEL_META):
                        if diff != last_diff: last_diff=diff; row_count=0
                        col_idx = row_count % cols
                        row_idx  = row_count // cols
                        gy = {"EASY":0,"MEDIUM":3,"HARD":7}[diff]*(bh+gap)
                        y  = 100 + gy + row_idx*(bh+gap) - scroll
                        x  = sx + col_idx*(bw+gap)
                        row_count += 1
                        if pygame.Rect(x,y,bw,bh).collidepoint(mx,my):
                            sel    = i
                            game   = Sokoban(load_level(i))
                            assets = load_assets(tile_size(game))
                            state  = "playing"
                            break

            elif state == "playing":
                if ev.type == pygame.KEYDOWN:
                    if   ev.key == pygame.K_UP:     game.move(0,-1)
                    elif ev.key == pygame.K_DOWN:   game.move(0, 1)
                    elif ev.key == pygame.K_LEFT:   game.move(-1,0)
                    elif ev.key == pygame.K_RIGHT:  game.move(1, 0)
                    elif ev.key == pygame.K_r:      game.reset()
                    elif ev.key == pygame.K_z:      game.undo()
                    elif ev.key == pygame.K_ESCAPE: state="menu"
                    if game and game.is_completed():
                        state = "completed"

            elif state == "completed":
                if ev.type == pygame.KEYDOWN:
                    if   ev.key == pygame.K_RETURN: state="menu"
                    elif ev.key == pygame.K_r:      game.reset(); state="playing"

        # Draw
        screen.fill(COL_BG)
        if state == "menu":
            cols, bw, bh, gap = 4, 190, 46, 12
            tw = cols*bw+(cols-1)*gap; sx=(WINDOW_WIDTH-tw)//2
            hover = -1; row_count = 0; last_diff = None
            for i,(name,diff) in enumerate(LEVEL_META):
                if diff!=last_diff: last_diff=diff; row_count=0
                col_idx=row_count%cols; row_idx=row_count//cols
                gy={"EASY":0,"MEDIUM":3,"HARD":7}[diff]*(bh+gap)
                y=100+gy+row_idx*(bh+gap)-scroll; x=sx+col_idx*(bw+gap)
                row_count+=1
                if pygame.Rect(x,y,bw,bh).collidepoint(mx,my): hover=i; break
            draw_menu(screen, scroll, hover)
        elif state == "playing":
            draw_grid(screen, game, assets, tile_size(game))
            draw_hud(screen, game, sel)
        elif state == "completed":
            draw_complete(screen, game, sel)

        pygame.display.flip()

if __name__ == "__main__":
    main()