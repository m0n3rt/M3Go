import pygame
import sys
import os
import random
import math
from pygame import gfxdraw
from game_utils import (
    set_input_method_to_english,
    GameData,
    get_current_input_method,
    restore_input_method,
    load_sound,
)
from achievement_system import achievement_system, ACHIEVEMENTS

# 初始化pygame
pygame.init()

# 游戏窗口设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Warrior Rimer")

pygame.font.init()

# 颜色与字体/资源定义
BACKGROUND = (20, 20, 35)
TEXT_COLOR = (220, 220, 220)
BUTTON_COLOR = (30, 90, 130)
BUTTON_HOVER_COLOR = (50, 140, 200)
BUTTON_TEXT_COLOR = (240, 240, 255)
COUNTDOWN_COLOR = (255, 215, 0)

title_font = pygame.font.SysFont(None, 48)
button_font = pygame.font.SysFont(None, 30)
countdown_font = pygame.font.SysFont(None, 120)

# 点击音效（若缺失则使用哑音效）
button_click_sound = load_sound('powerup.wav')

# 动态背景粒子系统
_BG_PARTICLES = None
_BG_PARTICLE_T = 0

def draw_background():
    global _BG_PARTICLES, _BG_PARTICLE_T
    # 初始化粒子（星点/光斑）
    if _BG_PARTICLES is None:
        _BG_PARTICLES = []
        for _ in range(40):
            px = random.uniform(0, WIDTH)
            py = random.uniform(0, HEIGHT)
            r = random.randint(10, 20)
            speed = random.uniform(0.15, 0.35)
            color = random.choice([(70,90,160),(100,120,200),(150,170,240),(230,240,255)])
            alpha = random.randint(70, 130)
            _BG_PARTICLES.append({
                'x': px, 'y': py, 'r': r, 'speed': speed, 'color': color, 'alpha': alpha,
                'phase': random.uniform(0, 6.28), 'twinkle': random.uniform(0.6, 1.2)
            })
    
    # 背景渐变
    screen.fill(BACKGROUND)
    # 轻微动态条纹（随时间上下流动）
    for i in range(0, HEIGHT, 4):
        base = 20 + int(10 * (i / HEIGHT))
        wobble = int(4 * math.sin(_BG_PARTICLE_T * 0.004 + i * 0.02))
        c = max(0, min(255, base + wobble))
        pygame.draw.line(screen, (c, c, min(255, c + 10)), (0, i), (WIDTH, i))
    
    # 动态粒子漂浮
    _BG_PARTICLE_T += 1
    for p in _BG_PARTICLES:
        # 漂浮运动：上下缓慢浮动+左右微摆
        p['y'] += p['speed'] * (0.6 + 0.4 * math.sin(_BG_PARTICLE_T * 0.010 + p['phase']))
        p['x'] += 0.30 * math.sin(_BG_PARTICLE_T * 0.014 + p['phase'] * 1.7)
        # 边界回环
        if p['y'] > HEIGHT + p['r']:
            p['y'] = -p['r']
            p['x'] = random.uniform(0, WIDTH)
        if p['x'] < -p['r']:
            p['x'] = WIDTH + p['r']
        if p['x'] > WIDTH + p['r']:
            p['x'] = -p['r']
        # 绘制粒子（光斑/星点）
        surf = pygame.Surface((p['r']*2, p['r']*2), pygame.SRCALPHA)
        twinkle = 0.7 + 0.3 * math.sin(_BG_PARTICLE_T * 0.02 * p['twinkle'] + p['phase'] * 0.9)
        for rr in range(p['r'], 0, -1):
            a = int(p['alpha'] * twinkle * (rr/p['r'])**2)
            pygame.draw.circle(surf, p['color'] + (a,), (p['r'], p['r']), rr)
        screen.blit(surf, (int(p['x']-p['r']), int(p['y']-p['r'])))
    
    # 叠加细微暗角（vignette）
    draw_vignette()


# 缓存的暗角表面
_VIGNETTE_SURF = None

def draw_vignette():
    global _VIGNETTE_SURF
    if _VIGNETTE_SURF is None:
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        thickness = 180
        # 顶/底 渐变
        for i in range(thickness):
            a = int(120 * (i / thickness))
            pygame.draw.line(surf, (0, 0, 0, a), (0, i), (WIDTH, i))
            pygame.draw.line(surf, (0, 0, 0, a), (0, HEIGHT - 1 - i), (WIDTH, HEIGHT - 1 - i))
        # 左/右 渐变
        for i in range(thickness):
            a = int(120 * (i / thickness))
            pygame.draw.line(surf, (0, 0, 0, a), (i, 0), (i, HEIGHT))
            pygame.draw.line(surf, (0, 0, 0, a), (WIDTH - 1 - i, 0), (WIDTH - 1 - i, HEIGHT))
        _VIGNETTE_SURF = surf
    screen.blit(_VIGNETTE_SURF, (0, 0))


def _lighten(color, d=20):
    r, g, b = color
    return (min(255, r + d), min(255, g + d), min(255, b + d))


def draw_fancy_button(rect, base_color, text_surface=None, border_color=(0, 100, 150)):
    # 阴影
    shadow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 60), shadow.get_rect(), border_radius=12)
    screen.blit(shadow, (rect.x, rect.y + 4))
    # 底色
    pygame.draw.rect(screen, base_color, rect, border_radius=12)
    # 顶部高光渐变
    overlay = pygame.Surface((rect.width, rect.height // 2 + 1), pygame.SRCALPHA)
    for y in range(overlay.get_height()):
        a = int(70 * (1 - y / max(1, overlay.get_height() - 1)))
        pygame.draw.line(overlay, (255, 255, 255, a), (0, y), (rect.width, y))
    screen.blit(overlay, rect.topleft)
    # 边框
    pygame.draw.rect(screen, border_color, rect, 3, border_radius=12)
    # 文本
    if text_surface is not None:
        screen.blit(text_surface, (rect.centerx - text_surface.get_width() // 2,
                                   rect.centery - text_surface.get_height() // 2))


def app_quit():
    global PREV_HKL
    try:
        # 恢复输入法（无论何种退出方式）
        if 'PREV_HKL' in globals():
            restore_input_method(PREV_HKL)
    except:
        pass
    finally:
        try:
            pygame.quit()
        finally:
            sys.exit(0)


def show_history_panel():
    # 历史记录面板：日期/难度/层数/分数
    back_btn = pygame.Rect(20, 20, 120, 50)
    header_font = pygame.font.SysFont(None, 26)
    row_font = pygame.font.SysFont(None, 24)

    def render_rows():
        hist = GameData.get_history()[::-1]  # 最近在上面
        rows = []
        for rec in hist:
            date = rec.get('date', '-')
            time_ = rec.get('time', '')
            diff = str(rec.get('difficulty', '-'))
            floor = str(rec.get('floor', '-'))
            score = str(rec.get('score', '-'))
            rows.append((f"{date} {time_}", diff, floor, score))
        return rows

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app_quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(pygame.mouse.get_pos()):
                    button_click_sound.play()
                    return

        draw_background()

        # 标题
        title = title_font.render("History", True, (255, 220, 120))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))

        # 返回按钮
        bh = back_btn.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (130, 130, 150) if bh else (100, 100, 120), back_btn, border_radius=10)
        pygame.draw.rect(screen, (160, 160, 180), back_btn, 3, border_radius=10)
        back_txt = button_font.render("BACK", True, BUTTON_TEXT_COLOR)
        screen.blit(back_txt, (back_btn.centerx - back_txt.get_width()//2, back_btn.centery - back_txt.get_height()//2))

        # 表头
        x0, y0 = 80, 140
        heads = ["Date", "Difficulty", "Floor", "Score"]
        xs = [x0, x0 + 260, x0 + 360, x0 + 460]
        for h, x in zip(heads, xs):
            screen.blit(header_font.render(h, True, (210, 230, 250)), (x, y0))
        pygame.draw.line(screen, (100, 120, 140), (x0 - 10, y0 + 28), (WIDTH - 80, y0 + 28), 2)

        # 内容
        rows = render_rows()
        if not rows:
            empty_msg = header_font.render("No records yet", True, (185, 195, 210))
            screen.blit(empty_msg, (WIDTH//2 - empty_msg.get_width()//2, y0 + 60))
        else:
            for i, (d, diff, fl, sc) in enumerate(rows):
                yy = y0 + 40 + i * 28
                screen.blit(row_font.render(d, True, (200, 210, 220)), (xs[0], yy))
                screen.blit(row_font.render(diff, True, (200, 210, 220)), (xs[1], yy))
                screen.blit(row_font.render(fl, True, (200, 210, 220)), (xs[2], yy))
                screen.blit(row_font.render(sc, True, (255, 230, 160)), (xs[3], yy))

        pygame.display.flip()
        pygame.time.delay(30)


def show_achievements_panel():
    """成就面板"""
    back_btn = pygame.Rect(20, 20, 120, 50)
    header_font = pygame.font.SysFont(None, 28)
    item_font = pygame.font.SysFont(None, 24)
    desc_font = pygame.font.SysFont(None, 20)
    
    scroll_y = 0
    max_scroll = max(0, len(ACHIEVEMENTS) * 120 - (HEIGHT - 200))
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app_quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(mouse_pos):
                    button_click_sound.play()
                    return
            if event.type == pygame.MOUSEWHEEL:
                scroll_y = max(0, min(max_scroll, scroll_y - event.y * 30))

        draw_background()

        # 标题
        title = title_font.render("Achievements", True, (255, 220, 120))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # 统计信息
        total_points = achievement_system.get_total_points()
        completion = achievement_system.get_completion_percentage()
        unlocked_count = len(achievement_system.get_unlocked_achievements())
        total_count = len(ACHIEVEMENTS)
        
        stats_text = header_font.render(f"Progress: {unlocked_count}/{total_count} ({completion:.1f}%) | Points: {total_points}", True, (200, 230, 255))
        screen.blit(stats_text, (WIDTH//2 - stats_text.get_width()//2, 90))

        # 返回按钮
        bh = back_btn.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (130, 130, 150) if bh else (100, 100, 120), back_btn, border_radius=10)
        pygame.draw.rect(screen, (160, 160, 180), back_btn, 3, border_radius=10)
        back_txt = button_font.render("BACK", True, BUTTON_TEXT_COLOR)
        screen.blit(back_txt, (back_btn.centerx - back_txt.get_width()//2, back_btn.centery - back_txt.get_height()//2))

        # 成就列表裁剪区域
        list_rect = pygame.Rect(40, 130, WIDTH - 80, HEIGHT - 180)
        prev_clip = screen.get_clip()
        screen.set_clip(list_rect)
        
        # 绘制成就项
        y_offset = 130 - scroll_y
        unlocked_achievements = achievement_system.get_unlocked_achievements()
        
        for i, (ach_id, ach_info) in enumerate(ACHIEVEMENTS.items()):
            item_y = y_offset + i * 120
            if item_y < 100 or item_y > HEIGHT + 50:
                continue
                
            item_rect = pygame.Rect(50, item_y, WIDTH - 100, 110)
            is_unlocked = ach_id in unlocked_achievements
            progress = achievement_system.get_achievement_progress(ach_id)
            
            # 背景
            bg_color = (40, 80, 40) if is_unlocked else (40, 40, 60)
            pygame.draw.rect(screen, bg_color, item_rect, border_radius=12)
            pygame.draw.rect(screen, (100, 150, 100) if is_unlocked else (80, 80, 120), item_rect, 3, border_radius=12)
            
            # 图标（用几何形状代替文字）
            icon_color = (255, 215, 0) if is_unlocked else (120, 120, 120)
            icon_bg_color = (60, 120, 60) if is_unlocked else (60, 60, 80)
            
            # 绘制图标背景圆形
            pygame.draw.circle(screen, icon_bg_color, (item_rect.left + 30, item_rect.top + 30), 18)
            pygame.draw.circle(screen, icon_color, (item_rect.left + 30, item_rect.top + 30), 18, 2)
            
            # 在圆形中绘制图标文字
            icon_surf = pygame.font.SysFont(None, 20).render(ach_info["icon"], True, icon_color)
            icon_text_rect = icon_surf.get_rect(center=(item_rect.left + 30, item_rect.top + 30))
            screen.blit(icon_surf, icon_text_rect)
            
            # 名称
            name_color = (150, 255, 150) if is_unlocked else (200, 200, 200)
            name_surf = item_font.render(ach_info["name"], True, name_color)
            screen.blit(name_surf, (item_rect.left + 70, item_rect.top + 15))
            
            # 点数
            points_surf = desc_font.render(f"{ach_info['points']} pts", True, (255, 215, 0))
            screen.blit(points_surf, (item_rect.right - 80, item_rect.top + 15))
            
            # 描述
            desc_surf = desc_font.render(ach_info["description"], True, (180, 180, 180))
            screen.blit(desc_surf, (item_rect.left + 70, item_rect.top + 45))
            
            # 进度条
            if not is_unlocked:
                progress_rect = pygame.Rect(item_rect.left + 70, item_rect.top + 75, 300, 8)
                pygame.draw.rect(screen, (60, 60, 60), progress_rect, border_radius=4)
                filled_rect = pygame.Rect(progress_rect.left, progress_rect.top, int(progress_rect.width * progress), progress_rect.height)
                pygame.draw.rect(screen, (100, 200, 100), filled_rect, border_radius=4)
                
                # 进度文字
                current_val = int(progress * ach_info["target"])
                progress_text = desc_font.render(f"{current_val}/{ach_info['target']}", True, (160, 160, 160))
                screen.blit(progress_text, (progress_rect.right + 10, progress_rect.top - 3))
            else:
                # 解锁日期
                unlock_info = achievement_system.achievements_data["unlocked"][ach_id]
                unlock_text = desc_font.render(f"Unlocked: {unlock_info['date']}", True, (120, 255, 120))
                screen.blit(unlock_text, (item_rect.left + 70, item_rect.top + 75))

        screen.set_clip(prev_clip)
        
        # 滚动条
        if max_scroll > 0:
            scrollbar_rect = pygame.Rect(WIDTH - 30, 130, 10, HEIGHT - 180)
            pygame.draw.rect(screen, (60, 60, 60), scrollbar_rect, border_radius=5)
            
            thumb_height = max(20, int((HEIGHT - 180) * (HEIGHT - 180) / (max_scroll + HEIGHT - 180)))
            thumb_y = 130 + int((scrollbar_rect.height - thumb_height) * (scroll_y / max_scroll))
            thumb_rect = pygame.Rect(WIDTH - 30, thumb_y, 10, thumb_height)
            pygame.draw.rect(screen, (120, 120, 120), thumb_rect, border_radius=5)

        pygame.display.flip()
        pygame.time.delay(30)


def show_risk_menu():
    # Risk 等级选择：滚轮样式，逆序（20 顶部 → 0 底部），可滚轮/方向键选择
    # 右侧效果预览扩大且不遮挡；选中后显示 START
    back_btn = pygame.Rect(20, 20, 120, 50)  # 左上角
    start_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT - 90, 200, 60)

    # 难度（20..0），包含零难度
    levels = list(range(20, -1, -1))  # [20,19,...,0]
    selected_index = 0  # 初始选中顶部（20）

    # 滚轮小窗口（仅显示 3 格）
    wheel_win = pygame.Rect(90, HEIGHT//2 - 60, 200, 220)
    wheel_center_x = wheel_win.centerx
    wheel_center_y = wheel_win.centery
    item_spacing = 66
    visible_half = 1  # 显示 3 个条目（选中上下各1）

    def level_to_risk(level: int) -> int:
        # 直接映射到 0..20 风险刻度（允许零难度）
        return max(0, min(20, int(level)))

    def risk_preview_lines(risk_val: int):
        # 与 main_game.RoguelikeManager.apply_risk_modifiers 对齐（12级后加速）
        n = max(0, min(20, int(risk_val)))
        extra = max(0, n - 12)
        enemy_hp = 1.0 + 0.02 * n + 0.01 * extra
        enemy_spd = 1.0 + 0.01 * n + 0.005 * extra
        player_dmg = max(0.6, 1.0 - (0.01 * n + 0.005 * extra))
        boss_hp = 1.0 + 0.03 * n + 0.015 * extra
        boss_imm = min(0.5, 0.02 * n + 0.005 * extra)
        radius = int(2 * n + 1 * extra)
        dmg = int(1 * n + 0.5 * extra)
        return [
            f"Enemy HP +{int((enemy_hp-1)*100)}%",
            f"Enemy Speed +{int((enemy_spd-1)*100)}%",
            f"Player Damage -{int((1-player_dmg)*100)}% (min -40%)",
            f"Boss HP +{int((boss_hp-1)*100)}%",
            f"Boss Immunity +{int(boss_imm*100)}% (adds to base)",
            f"Boss Explosion +{radius}px radius, +{dmg} dmg",
        ]
                                
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app_quit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    if selected_index > 0:
                        selected_index -= 1; button_click_sound.play()
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if selected_index < len(levels) - 1:
                        selected_index += 1; button_click_sound.play()
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    button_click_sound.play(); return level_to_risk(levels[selected_index])
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0 and selected_index > 0:
                    selected_index -= 1; button_click_sound.play()
                elif event.y < 0 and selected_index < len(levels) - 1:
                    selected_index += 1; button_click_sound.play()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(mouse_pos):
                    button_click_sound.play(); return level_to_risk(levels[selected_index])
                if back_btn.collidepoint(mouse_pos):
                    button_click_sound.play(); return None
                for i in range(-visible_half, visible_half + 1):
                    idx = selected_index + i
                    if 0 <= idx < len(levels):
                        y = wheel_center_y + i * item_spacing
                        rect = pygame.Rect(wheel_center_x - 60, y - 24, 120, 48)
                        if rect.collidepoint(mouse_pos):
                            selected_index = idx; button_click_sound.play(); break

        draw_background()

        # 标题承载面板 + 发光
        panel_rect = pygame.Rect(WIDTH//2 - 360, HEIGHT//4 - 40, 720, 120)
        panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 120, 220, 160), panel.get_rect(), border_radius=20)
        pygame.draw.rect(panel, (0, 160, 255, 200), panel.get_rect(), 4, border_radius=20)
        for i in range(6, 0, -1):
            glow = pygame.Surface((panel_rect.width + i*16, panel_rect.height + i*16), pygame.SRCALPHA)
            pygame.draw.rect(glow, (0, 120, 220, 18), glow.get_rect(), border_radius=26)
            screen.blit(glow, (panel_rect.centerx - glow.get_width()//2, panel_rect.centery - glow.get_height()//2))
        screen.blit(panel, panel_rect.topleft)
        title = title_font.render("Select Difficulty Level (0-20)", True, (255, 215, 0))
        screen.blit(title, (panel_rect.centerx - title.get_width()//2, panel_rect.centery - title.get_height()//2))
          
        # 左侧滚轮窗口背景
        window_bg = pygame.Surface(wheel_win.size, pygame.SRCALPHA)
        window_bg.fill((20, 30, 50, 140))
        pygame.draw.rect(window_bg, (80, 120, 160), window_bg.get_rect(), 2, border_radius=12)
        screen.blit(window_bg, wheel_win.topleft)

        # 启用裁剪
        prev_clip = screen.get_clip()
        screen.set_clip(wheel_win)

        # 左侧滚轮（逆序 20..0，高亮选中项，仅显示3项）
        current_level = levels[selected_index]
        t = max(0.0, min(1.0, current_level / 20.0))
        level_t = t * t * (3 - 2 * t)  # smoothstep
        for i in range(-visible_half, visible_half + 1):
            idx = selected_index + i
            if 0 <= idx < len(levels):
                y = wheel_center_y + i * item_spacing
                is_sel = (i == 0)
                w = 130 if is_sel else 110
                h = 52 if is_sel else 42
                x = wheel_center_x - w//2
                rect = pygame.Rect(x, y - h//2, w, h)
                hover = rect.collidepoint(mouse_pos)
                if is_sel:
                    gcol = (0, 200, 120); rcol = (200, 30, 30)
                    base_color = (
                        int(gcol[0] + (rcol[0] - gcol[0]) * level_t),
                        int(gcol[1] + (rcol[1] - gcol[1]) * level_t),
                        int(gcol[2] + (rcol[2] - gcol[2]) * level_t)
                    )
                else:
                    base_color = BUTTON_COLOR
                pygame.draw.rect(screen, base_color, rect, border_radius=10)
                pygame.draw.rect(screen, (0, 100, 150), rect, 3, border_radius=10)
                if hover:
                    glow = pygame.Surface((w+14, h+14), pygame.SRCALPHA)
                    pygame.draw.rect(glow, (0, 220, 255, 60), glow.get_rect(), border_radius=12)
                    screen.blit(glow, (rect.x-7, rect.y-7))
                label = button_font.render(str(levels[idx]), True, BUTTON_TEXT_COLOR)
                screen.blit(label, (rect.centerx - label.get_width()//2, rect.centery - label.get_height()//2))

        # 居中标记
        marker = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.polygon(marker, (180, 200, 255, 140), [(0,6),(6,0),(12,6),(6,12)])
        screen.blit(marker, (wheel_win.right - 18, wheel_center_y - 6))

        # 滚动提示箭头
        if selected_index > 0:
            up = pygame.Surface((18, 12), pygame.SRCALPHA)
            pygame.draw.polygon(up, (200, 220, 255, 180), [(9,2),(16,10),(2,10)])
            screen.blit(up, (wheel_center_x - 9, wheel_win.top + 6))
        if selected_index < len(levels) - 1:
            dn = pygame.Surface((18, 12), pygame.SRCALPHA)
            pygame.draw.polygon(dn, (200, 220, 255, 180), [(2,2),(16,2),(9,10)])
            screen.blit(dn, (wheel_center_x - 9, wheel_win.bottom - 18))

        # 关闭裁剪
        screen.set_clip(prev_clip)

        # 右侧效果预览
        lines = risk_preview_lines(level_to_risk(levels[selected_index]))
        preview_w = 440
        preview_h = 50 + len(lines) * 32 + 30
        preview_rect = pygame.Rect(WIDTH - preview_w - 20, wheel_center_y - preview_h//2 + 10, preview_w, preview_h)
        pygame.draw.rect(screen, (40, 60, 80, 160), preview_rect, border_radius=12)
        pygame.draw.rect(screen, (80, 120, 160), preview_rect, 2, border_radius=12)
        head = button_font.render("Effects", True, (220, 240, 255))
        screen.blit(head, (preview_rect.centerx - head.get_width()//2, preview_rect.top + 8))
        lf = pygame.font.SysFont(None, 26)
        for i, line in enumerate(lines):
            ts = lf.render(line, True, (200, 220, 240))
            screen.blit(ts, (preview_rect.left + 12, preview_rect.top + 50 + i*32))

        # 已选信息
        info_font = pygame.font.SysFont(None, 28)
        sel_level = levels[selected_index]
        risk_val = level_to_risk(sel_level)
        info = info_font.render(f"Selected: Level {sel_level}  (Risk {risk_val})", True, (220, 240, 255))
        screen.blit(info, (wheel_win.centerx - info.get_width()//2, wheel_win.bottom + 12))

        # Back 按钮
        back_hover = back_btn.collidepoint(mouse_pos)
        back_color = (130, 130, 150) if back_hover else (100, 100, 120)
        pygame.draw.rect(screen, back_color, back_btn, border_radius=10)
        pygame.draw.rect(screen, (160, 160, 180), back_btn, 3, border_radius=10)
        if back_hover:
            glow = pygame.Surface((back_btn.width+14, back_btn.height+14), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 255, 255, 40), glow.get_rect(), border_radius=14)
            screen.blit(glow, (back_btn.x-7, back_btn.y-7))
        back_txt = button_font.render("BACK", True, BUTTON_TEXT_COLOR)
        screen.blit(back_txt, (back_btn.centerx - back_txt.get_width()//2, back_btn.centery - back_txt.get_height()//2))

        # Start 按钮
        start_hover = start_btn.collidepoint(mouse_pos)
        gbase = (50, 180, 100); rbase = (200, 30, 30)
        tt = max(0.0, min(1.0, sel_level / 20.0)); tt = tt * tt * (3 - 2 * tt)
        start_base = (
            int(gbase[0] + (rbase[0] - gbase[0]) * tt),
            int(gbase[1] + (rbase[1] - gbase[1]) * tt),
            int(gbase[2] + (rbase[2] - gbase[2]) * tt)
        )
        if start_hover:
            start_color = (min(255, start_base[0] + 10), min(255, start_base[1] + 10), min(255, start_base[2] + 10))
        else:
            start_color = start_base
        pygame.draw.rect(screen, start_color, start_btn, border_radius=12)
        pygame.draw.rect(screen, (40, 120, 80), start_btn, 3, border_radius=12)
        if start_hover:
            glow = pygame.Surface((start_btn.width+16, start_btn.height+16), pygame.SRCALPHA)
            pygame.draw.rect(glow, (0, 220, 255, 60), glow.get_rect(), border_radius=16)
            screen.blit(glow, (start_btn.x-8, start_btn.y-8))
        start_txt = button_font.render("START", True, (255, 255, 255))
        screen.blit(start_txt, (start_btn.centerx - start_txt.get_width()//2, start_btn.centery - start_txt.get_height()//2))

        # 高难度提示（>=12）
        if sel_level >= 12:
            warn_font = pygame.font.SysFont(None, 28)
            warn_txt = warn_font.render("Challenging currently!", True, (255, 120, 120))
            screen.blit(warn_txt, (start_btn.centerx - warn_txt.get_width()//2 - 208, start_btn.top - warn_txt.get_height() - 280))

        pygame.display.flip(); pygame.time.delay(30)

def show_main_menu():
    start_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 40, 200, 60)
    history_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 60)
    achievements_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 60)
    continue_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 200, 200, 60)
    
    button_hover = [False, False, False, False]  # [start, history, achievements, continue]
    
    # 获取最高分
    high_score = GameData.get_high_score()
    
    # 检查是否有保存的游戏
    has_saved_game = GameData.has_saved_game()
    
    # 记录游戏启动（首次进入主菜单时）
    achievement_system.update_progress("game_start", 1)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        button_hover[0] = start_button.collidepoint(mouse_pos)
        button_hover[1] = history_button.collidepoint(mouse_pos)
        button_hover[2] = achievements_button.collidepoint(mouse_pos)
        button_hover[3] = continue_button.collidepoint(mouse_pos) and has_saved_game
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app_quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(mouse_pos):
                    button_click_sound.play()
                    risk = show_risk_menu()
                    if risk is None:
                        # 返回主菜单
                        continue
                    ok = show_countdown()
                    if ok:
                        return (False, {"type": "risk", "value": risk})
                if history_button.collidepoint(mouse_pos):
                    button_click_sound.play()  
                    show_history_panel()
                if achievements_button.collidepoint(mouse_pos):
                    button_click_sound.play()
                    show_achievements_panel()
                if continue_button.collidepoint(mouse_pos) and has_saved_game:
                    button_click_sound.play()
                    # 加载保存的游戏，继续无需选择难度，沿用存档状态（此处返回 None 难度，让 main 那边用 Normal 兜底）
                    return (True, None)

        draw_background()
        
        # 绘制标题
        title_text = title_font.render("Warrior Rimer", True, TEXT_COLOR)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4 - 40))
        
        # 绘制最高分和成就信息
        high_score_text = button_font.render(f"Highest Score: {high_score}", True, (255, 215, 0))
        screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//4 + 20))
        
        # 成就统计
        achievement_stats = button_font.render(f"Achievements: {len(achievement_system.get_unlocked_achievements())}/{len(ACHIEVEMENTS)} ({achievement_system.get_completion_percentage():.0f}%)", True, (150, 200, 255))
        screen.blit(achievement_stats, (WIDTH//2 - achievement_stats.get_width()//2, HEIGHT//4 + 50))
        
        # 绘制按钮（渐变玻璃风格）
        start_color = BUTTON_HOVER_COLOR if button_hover[0] else BUTTON_COLOR
        start_text = button_font.render("START", True, BUTTON_TEXT_COLOR)
        draw_fancy_button(start_button, start_color, start_text)
            
        # 绘制历史记录按钮
        history_color = BUTTON_HOVER_COLOR if button_hover[1] else BUTTON_COLOR
        history_text = button_font.render("HISTORY", True, BUTTON_TEXT_COLOR)
        draw_fancy_button(history_button, history_color, history_text)
        
        # 绘制成就按钮
        achievements_color = BUTTON_HOVER_COLOR if button_hover[2] else (80, 130, 180)
        achievements_text = button_font.render("ACHIEVEMENTS", True, BUTTON_TEXT_COLOR)
        draw_fancy_button(achievements_button, achievements_color, achievements_text, border_color=(120, 170, 220))
            
        # 绘制继续游戏按钮（如果有保存的游戏）
        if has_saved_game:
            continue_color = BUTTON_HOVER_COLOR if button_hover[3] else (200, 150, 50)
            continue_text = button_font.render("CONTINUE", True, BUTTON_TEXT_COLOR)
            draw_fancy_button(continue_button, continue_color, continue_text, border_color=(220,180,70))
        else:
            # 如果无保存的游戏，显示灰色按钮
            # 灰态不可用按钮也用同风格，但色彩偏灰
            disabled_color = (110, 110, 110)
            continue_text = button_font.render("CONTINUE", True, (200, 200, 200))
            draw_fancy_button(continue_button, disabled_color, continue_text, border_color=(140,140,140))
        
        # 绘制说明
        controls_font = pygame.font.SysFont(None, 24)
        controls_text = [
            "Controls:",
            "WASD - Move",
            "SPACE - Shoot", 
            "M - Pause Game",
            "1,2,3 - Switch Weapons",
            "F - Activate Attack Boost"
        ]
        
        for i, text in enumerate(controls_text):
            text_surface = controls_font.render(text, True, (160, 160, 180))
            screen.blit(text_surface, (WIDTH//2 + 120, 
                                     HEIGHT - 160 + i * 25))
        
        pygame.display.flip()
        pygame.time.delay(30)

# 倒计时
def show_countdown():
    countdown_values = [3, 2, 1]
    
    for count in countdown_values:
        for _ in range(60):  # 每秒钟60帧
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    app_quit()
            
            draw_background()

            # 绘制倒计时数字
            count_text = countdown_font.render(str(count), True, COUNTDOWN_COLOR)
            text_rect = count_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            
            # 添加发光效果
            glow_surface = pygame.Surface((text_rect.width + 40, text_rect.height + 40), pygame.SRCALPHA)
            for i in range(10, 0, -1):
                alpha = 100 - i * 10
                glow_color = (255, 215, 0, alpha)
                pygame.draw.circle(glow_surface, glow_color, 
                                  (glow_surface.get_width()//2, glow_surface.get_height()//2), 
                                  i * 3)
            
            screen.blit(glow_surface, (text_rect.centerx - glow_surface.get_width()//2, 
                                      text_rect.centery - glow_surface.get_height()//2))
            
            screen.blit(count_text, text_rect)
            
            pygame.display.flip()
            pygame.time.delay(16)  # 约60FPS
    
    return True

# 主函数
def main():
    global PREV_HKL
    # 记录并切换输入法为英文
    PREV_HKL = get_current_input_method()
    set_input_method_to_english()
    
    # 注册退出回调，确保强制关闭时也能恢复输入法
    import atexit
    def cleanup():
        try:
            restore_input_method(PREV_HKL)
        except:
            pass
    atexit.register(cleanup)
    
    # 主循环，允许从游戏返回后重新显示菜单
    try:
        while True:
            # 显示主菜单
            continue_saved, difficulty_info = show_main_menu()
            
            # 倒计时结束后启动游戏
            import main_game
            # 如果是继续游戏，加载保存的状态
            # 如果是继续游戏，难度可忽略；否则使用选择的难度
            if continue_saved:
                main_game.main(load_saved_state=True)
            else:
                # 兼容：如果是 Risk 选择，传入 dict；否则兜底 Normal
                main_game.main(load_saved_state=False, difficulty=(difficulty_info or "Normal"))
    except KeyboardInterrupt:
        # 处理 Ctrl+C
        pass
    except Exception as e:
        print(f"游戏出现错误: {e}")
    finally:
        # 程序即将退出时恢复输入法（保险）
        try:
            restore_input_method(PREV_HKL)
        except:
            pass

if __name__ == "__main__":
    main()


