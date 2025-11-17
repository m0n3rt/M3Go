# main_game.py
import pygame
import sys
import random
import math
import os
from game_utils import GameData, load_sound, set_input_method_to_english, get_current_input_method, restore_input_method
from achievement_system import achievement_system, ACHIEVEMENTS

# 初始化
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.mixer.set_num_channels(16)

# 窗口
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Warrior Rimer")

# 颜色
BACKGROUND = (20, 20, 35)
TEXT_COLOR = (220, 220, 220)
PLAYER_COLOR = (0, 200, 255)
ENEMY_COLOR = (255, 80, 80)
PLAYER_BULLET_COLOR = (255, 215, 0)
ENEMY_BULLET_COLOR = (255, 50, 50)
SHOTGUN_COLOR = (255, 150, 0)
GRENADE_COLOR = (100, 255, 100)
GRENADE_EXPLOSION_COLOR = (255, 200, 0)
WALL_COLOR = (100, 100, 120)
UI_BG = (30, 30, 50, 180)
BOSS_COLOR = (180, 50, 180)
BOSS_EXPLOSION_COLOR = (255, 100, 255)
FLOAT_TEXT_COLOR_ENEMY = (255, 220, 120)
FLOAT_TEXT_COLOR_BOSS = (255, 180, 255)
FLOAT_TEXT_COLOR_PLAYER = (255, 100, 100)

# 音效
shoot_sounds = [
    load_sound("shoot1.wav"),   # 手枪
    load_sound("shoot2.wav"),   # 霰弹
    load_sound("grenade_throw.wav"),  # 手雷
]
explosion_sound = load_sound("explosion.wav")
enemy_shoot_sound = load_sound("enemy_shoot.wav")
player_hit_sound = load_sound("player_hit.wav")
powerup_sound = load_sound("powerup.wav")
weapon_switch_sound = load_sound("weapon_switch.wav")
skill_activate_sound = load_sound("skill_activate.wav")
boss_spawn_sound = load_sound("striking.wav")
boss_roar_sound = load_sound("roar.wav")

for s in shoot_sounds: s.set_volume(0.4)
explosion_sound.set_volume(0.6)
enemy_shoot_sound.set_volume(0.3)
player_hit_sound.set_volume(0.5)
powerup_sound.set_volume(0.5)
weapon_switch_sound.set_volume(0.4)
skill_activate_sound.set_volume(0.5)
boss_spawn_sound.set_volume(0.9)
boss_roar_sound.set_volume(0.8)

# 漂浮文字小字体
float_font = pygame.font.SysFont(None, 22)

# 预创建常用字体，避免每帧频繁构造
FONT_48 = pygame.font.SysFont(None, 48)
FONT_36 = pygame.font.SysFont(None, 36)
FONT_32 = pygame.font.SysFont(None, 32)
FONT_30 = pygame.font.SysFont(None, 30)
FONT_28 = pygame.font.SysFont(None, 28)
FONT_24 = pygame.font.SysFont(None, 24)

# 轻量对象池，减少频繁创建/销毁带来的压力
# 全局池与节流变量（用于性能优化）
_PARTICLE_POOL = []
_FLOAT_TEXT_POOL = []
_EXPLOSION_SND_NEXT_TICK = 0
# 暂停菜单
class PauseMenu:
    def __init__(self):
        self.visible = False
        self.continue_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 60)
        self.quit_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60)

    def draw(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        menu_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 100, 300, 250)
        pygame.draw.rect(screen, (40, 40, 80), menu_rect, border_radius=15)
        pygame.draw.rect(screen, (80, 80, 120), menu_rect, 3, border_radius=15)

        title = FONT_48.render("PAUSED", True, (255, 215, 0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 130))

        mouse_pos = pygame.mouse.get_pos()
        cont_hover = self.continue_button.collidepoint(mouse_pos)
        quit_hover = self.quit_button.collidepoint(mouse_pos)

        cont_color = (100, 200, 100) if cont_hover else (70, 160, 70)
        pygame.draw.rect(screen, cont_color, self.continue_button, border_radius=10)
        pygame.draw.rect(screen, (150, 250, 150), self.continue_button, 3, border_radius=10)
        cont_text = FONT_36.render("CONTINUE", True, (255, 255, 255))
        screen.blit(cont_text, (self.continue_button.centerx - cont_text.get_width()//2, self.continue_button.centery - cont_text.get_height()//2))

        quit_color = (200, 100, 100) if quit_hover else (160, 70, 70)
        pygame.draw.rect(screen, quit_color, self.quit_button, border_radius=10)
        pygame.draw.rect(screen, (250, 150, 150), self.quit_button, 3, border_radius=10)
        quit_text = FONT_36.render("QUIT", True, (255, 255, 255))
        screen.blit(quit_text, (self.quit_button.centerx - quit_text.get_width()//2, self.quit_button.centery - quit_text.get_height()//2))

        info_text = FONT_24.render("Progress saved automatically", True, (180, 180, 200))
        screen.blit(info_text, (WIDTH//2 - info_text.get_width()//2, HEIGHT//2 + 120))

    def handle_event(self, event, player, enemies, score):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.continue_button.collidepoint(event.pos):
                self.visible = False
                return True
            if self.quit_button.collidepoint(event.pos):
                GameData.save_game_state({
                    "player": {
                        "x": player.x, "y": player.y, "health": player.health,
                        "shield": player.shield, "weapon": player.weapon, "score": player.score,
                        "attack_boost_active": player.attack_boost_active,
                        "attack_boost_duration": player.attack_boost_duration,
                        "attack_boost_cooldown": player.attack_boost_cooldown,
                        "grenade_cooldown": player.grenade_cooldown,
                        "fire_binding": getattr(player, 'fire_binding', 'space')
                    },
                    "enemies": [{"x": e.x, "y": e.y, "health": e.health} for e in enemies],
                    "score": score
                })
                return False
        return True

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 80
        self.radius = 20
        self.color = PLAYER_COLOR
        self.speed = 2.5
        self.health = 100
        self.max_health = 100
        self.shield = 0
        self.shield_max = 60
        self.flash = 0
        self.weapon = 0
        self.weapon_names = ["Pistol", "Shotgun", "Grenade"]
        self.gun_cooldown = 0
        self.grenade_cooldown = 0
        self.attack_boost_active = False
        self.attack_boost_duration = 0
        self.attack_boost_cooldown = 0
        self.collision_cooldown = 0
        self.bullet_damage = 10
        self.score = 0
        self.gold = 0
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)
        # 战前选择技能（F键释放）：'rapid' | 'fortify' | 'triple'
        self.selected_skill = None
        # 非 rapid 技能使用该冷却；rapid 使用 attack_boost_cooldown
        self.skill_cooldown = 0
        # 控制方案：'space'（空格开火，默认）或 'mouse'（鼠标左键开火）
        self.fire_binding = 'space'

    def add_gold(self, amount:int):
        self.gold += amount

    def spend_gold(self, amount:int) -> bool:
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        if self.shield > 0:
            shield_alpha = int(150 * (self.shield / self.shield_max))
            pygame.draw.circle(screen, (100, 200, 255, shield_alpha), (self.x, self.y), self.radius + 8, 3)
        if self.flash > 0:
            pygame.draw.circle(screen, (255, 255, 255, 80), (self.x, self.y), self.radius + 2, 2)

    def move(self, keys, walls):
        dx = (keys[pygame.K_d] - keys[pygame.K_a]) * self.speed
        dy = (keys[pygame.K_s] - keys[pygame.K_w]) * self.speed
        if dx or dy:
            # 预计算目标位置并限制在屏幕边界内
            nx = min(max(self.radius, self.x + dx), WIDTH - self.radius)
            ny = min(max(self.radius, self.y + dy), HEIGHT - self.radius)
            new_rect = pygame.Rect(nx - self.radius, ny - self.radius, self.radius*2, self.radius*2)
            # 避开墙体碰撞
            if not any(new_rect.colliderect(w.rect) for w in walls):
                self.x = nx; self.y = ny
                self.rect.topleft = (self.x - self.radius, self.y - self.radius)

    def shoot(self, bullets, grenades):
        mult = 0.5 if self.attack_boost_active and self.weapon != 2 else 1.0
        # Pistol
        if self.weapon == 0 and self.gun_cooldown == 0:
            if hasattr(bullets, 'add'):
                bullets.add(Bullet(self.x, self.y - 30, -10, PLAYER_BULLET_COLOR, "player"))
            else:
                bullets.append(Bullet(self.x, self.y - 30, -10, PLAYER_BULLET_COLOR, "player"))
            self.gun_cooldown = int(15 * mult)
            shoot_sounds[0].play(); return True
        # Shotgun
        if self.weapon == 1 and self.gun_cooldown == 0:
            if hasattr(bullets, 'add'):
                bullets.add(Bullet(self.x - 10, self.y - 30, -10, SHOTGUN_COLOR, "player", 8))
                bullets.add(Bullet(self.x, self.y - 30, -12, SHOTGUN_COLOR, "player", 8))
                bullets.add(Bullet(self.x + 10, self.y - 30, -10, SHOTGUN_COLOR, "player", 8))
            else:
                bullets.append(Bullet(self.x - 10, self.y - 30, -10, SHOTGUN_COLOR, "player", 8))
                bullets.append(Bullet(self.x, self.y - 30, -12, SHOTGUN_COLOR, "player", 8))
                bullets.append(Bullet(self.x + 10, self.y - 30, -10, SHOTGUN_COLOR, "player", 8))
            self.gun_cooldown = int(30 * mult)
            shoot_sounds[1].play(); return True
        # Grenade
        if self.weapon == 2 and self.gun_cooldown == 0 and self.grenade_cooldown == 0:
            if hasattr(grenades, 'add'):
                grenades.add(Grenade(self.x, self.y - 30, -8, GRENADE_COLOR, "player"))
            else:
                grenades.append(Grenade(self.x, self.y - 30, -8, GRENADE_COLOR, "player"))
            self.gun_cooldown = 20; self.grenade_cooldown = 600
            shoot_sounds[2].play(); return True
        return False

    def update_skills(self):
        if self.flash > 0:
            self.flash -= 1
        if self.attack_boost_active:
            self.attack_boost_duration -= 1
            if self.attack_boost_duration <= 0:
                self.attack_boost_active = False
        if self.attack_boost_cooldown > 0:
            self.attack_boost_cooldown -= 1
        if self.skill_cooldown > 0:
            self.skill_cooldown -= 1
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1
        if self.gun_cooldown > 0:
            self.gun_cooldown -= 1
        if self.grenade_cooldown > 0:
            self.grenade_cooldown -= 1

    def activate_attack_boost(self):
        if self.attack_boost_cooldown == 0:
            self.attack_boost_active = True
            self.attack_boost_duration = 300
            self.attack_boost_cooldown = 900
            return True
        return False

    def switch_weapon(self, direction):
        self.weapon = (self.weapon + direction) % 3
        if self.weapon < 0: self.weapon = 2
        weapon_switch_sound.play()

    def add_shield(self, amount):
        self.shield = min(self.shield_max, self.shield + amount)

    def take_damage(self, amount:int):
        # 先用护盾吸收，再扣生命；触发受击闪烁与音效
        try:
            dmg = max(0, int(amount))
        except:
            dmg = 0
        if dmg <= 0:
            return
        if self.shield > 0:
            absorbed = min(self.shield, dmg)
            self.shield -= absorbed
            dmg -= absorbed
        if dmg > 0:
            self.health = max(0, self.health - dmg)
            self.flash = 10
            try:
                player_hit_sound.play()
            except:
                pass

    def get_effective_damage(self, base:int, rl_manager=None) -> int:
        dmg = float(base)
        # 攻击加成（技能/永久）
        if self.attack_boost_active:
            dmg *= 1.5
        if rl_manager is not None:
            dmg *= max(0.1, rl_manager.player_damage_mult)
            dmg *= (1.0 + rl_manager.player_permanent_bonuses.get('damage_bonus', 0.0))
        return max(1, int(dmg))

    def get_grenade_damage(self, rl_manager=None) -> int:
        base = 50
        if rl_manager is not None:
            base += rl_manager.player_permanent_bonuses.get('grenade_damage_bonus', 0)
            base *= max(0.1, rl_manager.player_damage_mult)
        if self.attack_boost_active:
            base *= 1.2
        return max(1, int(base))

    # 技能释放接口（F键）
    def activate_selected_skill(self, bullets):
        if not self.selected_skill:
            return False
        # 技能一：攻速提升
        if self.selected_skill == 'rapid':
            return self.activate_attack_boost()
        # 技能二：护盾+治疗
        if self.selected_skill == 'fortify':
            if self.skill_cooldown > 0:
                return False
            self.health = min(self.max_health, self.health + 40)
            self.add_shield(40)
            powerup_sound.play()
            self.skill_cooldown = 900  # 15s
            return True
        # 技能三：三轮扇形霰弹（锥形弹幕）
        if self.selected_skill == 'triple':
            if self.skill_cooldown > 0:
                return False
            def fire_cone(center_x, center_y, total_angle_deg=40, pellets=7, base_speed=11):
                # -total/2 到 +total/2 等间距发射
                if pellets <= 1:
                    angles = [0.0]
                else:
                    start = -total_angle_deg/2
                    step = total_angle_deg/(pellets-1)
                    angles = [start + i*step for i in range(pellets)]
                for ang in angles:
                    rad = math.radians(ang)
                    vx = base_speed * math.sin(rad)
                    vy = -base_speed * math.cos(rad)  # 向上为负
                    if hasattr(bullets, 'add'):
                        bullets.add(Bullet(center_x, center_y, vy, SHOTGUN_COLOR, 'player', 6, dx=vx, dy=vy))
                    else:
                        bullets.append(Bullet(center_x, center_y, vy, SHOTGUN_COLOR, 'player', 6, dx=vx, dy=vy))
            # 十轮，角度与速度逐步增加，形成更强的覆盖与层次
            for i in range(10):
                t = i / 9.0  # 0..1
                angle = int(36 + 24 * t)   # 36° -> 60°
                speed = 11 + int(2 * t)    # 11 -> 13
                fire_cone(self.x, self.y - 30, total_angle_deg=angle, pellets=7, base_speed=speed)
            shoot_sounds[1].play()
            self.skill_cooldown = 900  # 15s
            return True
        return False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, walls):
        super().__init__()
        self.radius = 18
        self.speed = random.uniform(1.0, 2.5)
        self.shoot_cooldown = random.randint(30, 120)
        self.color = (random.randint(200, 255), random.randint(50, 100), random.randint(50, 100))
        self.health = 50
        self.max_health = 50
        self.direction = random.choice([-1, 1])
        self.collision_cooldown = 0
        self.flash = 0
        valid = False; tries = 0
        while not valid and tries < 100:
            tries += 1
            self.x = random.randint(self.radius, WIDTH - self.radius)
            self.y = random.randint(self.radius, HEIGHT // 2)
            r = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)
            valid = not any(r.colliderect(w.rect) for w in walls)
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)

    def draw(self, player):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        # 眼睛
        eye_offset = 6
        pygame.draw.circle(screen, (255, 255, 255), (self.x - eye_offset, self.y - 5), 5)
        pygame.draw.circle(screen, (255, 255, 255), (self.x + eye_offset, self.y - 5), 5)
        ang = math.atan2(player.y - self.y, player.x - self.x)
        pupil = 2
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x - eye_offset + pupil*math.cos(ang)), int(self.y - 5 + pupil*math.sin(ang))), 2)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + eye_offset + pupil*math.cos(ang)), int(self.y - 5 + pupil*math.sin(ang))), 2)
        # 血条
        bw, bh = 40, 5
        hp = self.health / self.max_health
        pygame.draw.rect(screen, (100, 0, 0), (self.x - bw//2, self.y + self.radius + 5, bw, bh))
        pygame.draw.rect(screen, (0, 200, 0), (self.x - bw//2, self.y + self.radius + 5, bw*hp, bh))

    def move(self, walls, player):
        dx = self.speed * self.direction
        new_rect = pygame.Rect(self.x - self.radius + dx, self.y - self.radius, self.radius*2, self.radius*2)
        if any(new_rect.colliderect(w.rect) for w in walls):
            # 撞到墙体，反向
            self.direction *= -1
        else:
            self.x += dx
        # 边缘反弹与回退，避免粘边
        if self.x <= self.radius:
            self.x = self.radius
            self.direction = 1
            self.x += self.speed  # 轻微回退，脱离边缘
        elif self.x >= WIDTH - self.radius:
            self.x = WIDTH - self.radius
            self.direction = -1
            self.x -= self.speed
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))
        # 撞玩家
        if self.collision_cooldown == 0:
            dist = math.hypot(self.x - player.x, self.y - player.y)
            if dist < self.radius + player.radius:
                player.take_damage(5); self.health -= 10
                self.collision_cooldown = 30; player.collision_cooldown = 30
                if self.health <= 0:
                    return True, False, True
                if player.health <= 0:
                    return True, True, False
                return True, False, False
        else:
            self.collision_cooldown -= 1
        return False, False, False

    def shoot(self, enemy_bullets):
        if self.shoot_cooldown <= 0:
            if hasattr(enemy_bullets, 'add'):
                enemy_bullets.add(Bullet(self.x, self.y + 30, 5, ENEMY_BULLET_COLOR, "enemy"))
            else:
                enemy_bullets.append(Bullet(self.x, self.y + 30, 5, ENEMY_BULLET_COLOR, "enemy"))
            self.shoot_cooldown = random.randint(60, 180)
            enemy_shoot_sound.play(); return True
        return False

    def collide_with_player(self, player):
        return math.hypot(self.x - player.x, self.y - player.y) < self.radius + player.radius

    # 亡语钩子（默认无）
    def on_death(self, player, particles, enemies=None):
        pass

class Bomber(Enemy):
    """亡语自爆敌人：死亡时在小范围内造成伤害（随风险增强，伤害可连锁波及其他敌人）"""
    def __init__(self, walls, rl=None):
        super().__init__(walls)
        r = getattr(rl, 'risk', 0) or 0
        self.color = (255, 140, 0)
        self.max_health = int(self.max_health * 0.8)
        self.health = self.max_health
        # 风险越高，半径/伤害越高
        self.death_explode_radius = 80 + int(1.5 * r)
        self.death_explode_damage = 18 + int(0.6 * r)

    def draw(self, player):
        super().draw(player)
        # 标记环
        pygame.draw.circle(screen, (255, 180, 80), (self.x, self.y), self.radius+4, 2)

    def on_death(self, player, particles, enemies=None):
        # 自身爆炸效果
        create_explosion(particles, self.x, self.y, 1.2)
        # 对玩家结算
        if math.hypot(player.x - self.x, player.y - self.y) < self.death_explode_radius + player.radius:
            player.take_damage(self.death_explode_damage)
            spawn_floating_text(particles, player.x, player.y - player.radius - 8, self.death_explode_damage, FLOAT_TEXT_COLOR_PLAYER)
        if enemies is None:
            return
        # 对周围敌人结算（可能连锁）
        for other in list(enemies):
            if other is self:
                continue
            try:
                if math.hypot(other.x - self.x, other.y - self.y) < self.death_explode_radius + getattr(other, 'radius', 0):
                    other.health -= self.death_explode_damage
                    spawn_floating_text(particles, other.x, other.y - other.radius - 8, self.death_explode_damage, FLOAT_TEXT_COLOR_ENEMY)
                    if other.health <= 0:
                        create_explosion(particles, other.x, other.y, 1.0)
                        try:
                            other.on_death(player, particles, enemies)
                        except:
                            pass
                        if other in enemies:
                            enemies.remove(other)
                        player.score += 10
                        player.add_gold(5)
                        spawn_floating_text(particles, other.x, other.y, "+5g", (255, 215, 0))
                        achievement_system.update_progress("kill_count", 1)
            except:
                continue

class Charger(Enemy):
    """爆破手：随机进入冲锋状态，移动一定距离后爆炸造成高伤害（随风险增强/冷却缩短）"""
    def __init__(self, walls, rl=None):
        super().__init__(walls)
        r = getattr(rl, 'risk', 0) or 0
        self.color = (200, 60, 255)
        self.max_health = int(self.max_health * 0.9)
        self.health = self.max_health
        self.is_charging = False
        # 风险加速冲锋速度
        self.charge_speed = 6.0 + 0.15 * r
        self.charge_dir = (0.0, 0.0)
        self.charge_travel = 0.0
        self.charge_distance = 260.0
        # 风险越高，进入冲锋的冷却越短
        lo = max(40, 120 - 3 * r)
        hi = max(80, 240 - 5 * r)
        if hi < lo: hi = lo
        self.charge_cooldown = random.randint(lo, hi)
        # 爆炸随风险增强
        self.explode_radius = 110 + int(1.5 * r)
        self.explode_damage = 26 + int(0.8 * r)

    def draw(self, player):
        # 充能时颜色闪烁
        c = (230, 130, 255) if self.is_charging and (pygame.time.get_ticks() // 120) % 2 == 0 else self.color
        pygame.draw.circle(screen, c, (self.x, self.y), self.radius)
        # 提示环
        ring_c = (255, 100, 200) if self.is_charging else (160, 80, 180)
        pygame.draw.circle(screen, ring_c, (self.x, self.y), self.radius+6, 2)
        # 血条
        bw, bh = 40, 5
        hp = self.health / self.max_health
        pygame.draw.rect(screen, (100, 0, 0), (self.x - bw//2, self.y + self.radius + 5, bw, bh))
        pygame.draw.rect(screen, (0, 200, 0), (self.x - bw//2, self.y + self.radius + 5, bw*hp, bh))

    def move(self, walls, player):
        # 返回 (collided_with_player, player_died, enemy_died)
        if self.is_charging:
            # 朝 charge_dir 直线推进
            step = self.charge_speed
            nx = self.x + self.charge_dir[0] * step
            ny = self.y + self.charge_dir[1] * step
            # 边界限制
            nx = min(max(self.radius, nx), WIDTH - self.radius)
            ny = min(max(self.radius, ny), HEIGHT - self.radius)
            new_rect = pygame.Rect(nx - self.radius, ny - self.radius, self.radius*2, self.radius*2)
            if any(new_rect.colliderect(w.rect) for w in walls):
                # 撞墙提前引爆
                self._explode(player)
                return False, False, True
            self.x = nx; self.y = ny
            self.rect.topleft = (self.x - self.radius, self.y - self.radius)
            self.charge_travel += step
            # 撞玩家直接引爆
            if self.collide_with_player(player):
                self._explode(player)
                return True, player.health <= 0, True
            # 距离达到阈值则自爆
            if self.charge_travel >= self.charge_distance:
                self._explode(player)
                return False, player.health <= 0, True
            return False, False, False
        else:
            # 普通游走（沿用父类横向移动），并倒计时进入冲锋
            col, player_died, enemy_died = super().move(walls, player)
            if self.charge_cooldown > 0:
                self.charge_cooldown -= 1
            else:
                # 进入冲锋，朝玩家方向
                ang = math.atan2(player.y - self.y, player.x - self.x)
                self.charge_dir = (math.cos(ang), math.sin(ang))
                self.is_charging = True
                self.charge_travel = 0.0
            return col, player_died, enemy_died

    def _explode(self, player):
        # 直接在当前位置爆炸并结算伤害
        explosion_sound.play()
        # 粒子由外层 create_explosion 更丰富，因此这里交给工具函数
        # 在外层调用位置没有直接调用，这里自己触发基本粒子
        try:
            # 延用全局粒子组不可得，这里仅对玩家结算
            if math.hypot(player.x - self.x, player.y - self.y) < self.explode_radius + player.radius:
                player.take_damage(self.explode_damage)
        except:
            pass

def spawn_random_enemy(walls, rl):
    """按权重生成敌人类型，随楼层/风险略调权重"""
    base = [
        (Enemy, 0.6),
        (Bomber, 0.25),
        (Charger, 0.15)
    ]
    # 楼层影响（6层后更多特种）
    if rl.floor >= 6:
        base = [(Enemy, 0.5), (Bomber, 0.3), (Charger, 0.2)]
    # 风险动态权重调整
    risk = getattr(rl, 'risk', 0) or 0
    w_enemy = base[0][1] - 0.01 * risk
    w_bomber = base[1][1] + 0.005 * risk
    w_charger = base[2][1] + 0.005 * risk
    # 限定最小/最大并归一化
    w_enemy = max(0.05, w_enemy)
    w_bomber = max(0.05, w_bomber)
    w_charger = max(0.05, w_charger)
    s = (w_enemy + w_bomber + w_charger)
    w_enemy, w_bomber, w_charger = w_enemy/s, w_bomber/s, w_charger/s
    weighted = [(Enemy, w_enemy), (Bomber, w_bomber), (Charger, w_charger)]
    rnum = random.random(); acc = 0.0
    for cls, w in weighted:
        acc += w
        if rnum <= acc:
            if cls is Enemy:
                return Enemy(walls)
            elif cls is Bomber:
                return Bomber(walls, rl)
            else:
                return Charger(walls, rl)
    return Enemy(walls)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color, owner, size=5, dx=None, dy=None):
        super().__init__()
        self.x = x; self.y = y
        self.radius = size
        # 兼容：旧代码使用 speed 表示纵向速度；新代码可传入 dx/dy 表示方向速度
        self.speed = speed
        self.vx = 0 if dx is None else dx
        self.vy = speed if dy is None else dy
        self.color = color
        self.owner = owner  # "player" 或 "enemy"
        self.trail = []
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)

    def draw(self):
        if self.owner == "player":
            for i, pos in enumerate(reversed(self.trail)):
                alpha = 200 - i*40
                size = max(1, int(self.radius * (1 - i/max(1, len(self.trail)))))
                pygame.draw.circle(screen, (*self.color, max(0, alpha)), pos, size)
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
            pygame.draw.circle(screen, (255, 255, 255), (self.x - 2, self.y - 2), max(1, self.radius // 2))
        else:
            pygame.draw.circle(screen, (255, 100, 100, 150), (self.x, self.y), self.radius + 2)
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
            pygame.draw.circle(screen, (255, 150, 150), (self.x, self.y), max(1, self.radius // 2))

    def move(self):
        # 支持斜向移动（霰弹锥形）
        self.x += self.vx
        self.y += self.vy
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5: self.trail.pop(0)

    def off_screen(self):
        # 出界判定包含左右边界，留少量缓冲
        return (self.y < -20 or self.y > HEIGHT + 20 or self.x < -20 or self.x > WIDTH + 20)

    def collide_with_player(self, player):
        return math.hypot(self.x - player.x, self.y - player.y) < self.radius + player.radius

    def collide_with_enemy(self, enemy):
        return math.hypot(self.x - enemy.x, self.y - enemy.y) < self.radius + enemy.radius

    def collide_with_wall(self, wall):
        r = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)
        return r.colliderect(wall.rect)

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color, owner):
        super().__init__()
        self.x = x; self.y = y
        self.radius = 8
        self.speed = speed
        self.color = color
        self.owner = owner
        self.exploded = False
        self.explosion_radius = 155
        self.explosion_damage = 50
        self.trail = []
        self.warning_timer = 30
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)
        # 仅按飞行距离触发爆炸
        self.fly_distance = 0
        self.max_distance = 320  # 手雷飞行距离（像素）
        # 为了保留闪烁提示，仍保留一个用于 UI 的倒计时（不再决定爆炸触发）
        self.timer = int(self.max_distance / max(1, abs(self.speed)))

    def draw(self):
        for i, pos in enumerate(self.trail):
            alpha = int(200 * (1 - i/max(1, len(self.trail))))
            pygame.draw.circle(screen, (*self.color, alpha), pos, max(1, int(self.radius * (1 - i/max(1,len(self.trail))))))
        if not self.exploded:
            t = max(0, self.timer)
            flash = (t < self.warning_timer and ((t // 3) % 2 == 0))
            c = (255, 100, 100) if flash else self.color
            pygame.draw.circle(screen, c, (self.x, self.y), self.radius)
            pygame.draw.circle(screen, (200, 200, 200), (self.x, self.y), self.radius - 2)
            pygame.draw.rect(screen, (150, 150, 150), (self.x - 2, self.y - 10, 4, 6))
        else:
            pygame.draw.circle(screen, GRENADE_EXPLOSION_COLOR, (self.x, self.y), self.explosion_radius // 2)

    def update(self):
        if not self.exploded:
            self.y += self.speed
            self.trail.append((self.x, self.y))
            if len(self.trail) > 5:
                self.trail.pop(0)
            # 距离累计，用于决定爆炸时机
            self.fly_distance += abs(self.speed)
            # 定时仅用于闪烁提示
            if self.timer > 0:
                self.timer -= 1
            # 仅当飞行达到设定距离才爆炸
            if self.fly_distance >= self.max_distance:
                self.exploded = True; return True
        return False

    def check_explosion_collision(self, entities):
        damaged = []
        if self.exploded:
            for e in entities:
                if math.hypot(self.x - e.x, self.y - e.y) < self.explosion_radius + getattr(e, 'radius', 0):
                    damaged.append(e)
        return damaged

class Boss:
    def __init__(self, rl=None):
        self.radius = 45
        self.x = WIDTH // 2
        self.y = HEIGHT // 4
        self.speed_x = random.choice([-3, 3])
        self.speed_y = random.choice([-3, 3])
        # 获取BOSS等级（用于属性增强）
        boss_level = rl.get_boss_level() if rl else 1
        # 根据风险/难度和BOSS等级调整Boss属性
        bh_mult = getattr(rl, 'boss_health_mult', 1.0) if rl else 1.0
        level_mult = 1.0 + (boss_level - 1) * 0.5  # 每等级+50%生命值
        # Boss生命值平衡：原先x300过于耗时，按需求下调60% -> 使用x120
        # 若后续仍感觉偏肉，可再降到x90；若偏脆，可在此基础上引入阶段护盾而不是继续堆HP
        self.max_health = int(500 * 120 * bh_mult * level_mult)
        self.health = self.max_health
        self.explosion_timer = 420
        self.explosion_cooldown = 0
        self.flash = 0
        self.collision_cooldown = 0
        extra_immune = getattr(rl, 'boss_immune_bonus', 0.0) if rl else 0.0
        self.immune_chance = min(0.8, max(0.0, 0.2 + extra_immune))
        self.spawn_effect_timer = 60
        self.is_charging = False
        self.charge_timer = 0
        self.charge_direction = (0, 0)
        self.charge_speed = 8
        self.charge_cooldown = 0
        self._rl = rl

    def draw(self):
        if self.spawn_effect_timer > 0:
            pulse = abs(math.sin(self.spawn_effect_timer * 0.1)) * 10
            color = (min(255, 180 + int(pulse * 7)), 50, min(255, 180 + int(pulse * 7)))
            pygame.draw.circle(screen, color, (self.x, self.y), self.radius + int(pulse))
            pygame.draw.circle(screen, BOSS_COLOR, (self.x, self.y), self.radius)
        else:
            color = (255, 255, 200) if self.flash > 0 else BOSS_COLOR
            if self.flash > 0: self.flash -= 1
            pygame.draw.circle(screen, color, (self.x, self.y), self.radius)
            pygame.draw.circle(screen, (100, 0, 100), (self.x, self.y), self.radius - 8)
            pygame.draw.circle(screen, (255, 50, 50), (self.x - 15, self.y - 10), 12)
            pygame.draw.circle(screen, (255, 50, 50), (self.x + 15, self.y - 10), 12)
            pygame.draw.circle(screen, (0, 0, 0), (self.x - 15, self.y - 10), 6)
            pygame.draw.circle(screen, (0, 0, 0), (self.x + 15, self.y - 10), 6)
            pygame.draw.polygon(screen, (150, 0, 150), [(self.x - 20, self.y - 40),(self.x - 30, self.y - 60),(self.x - 10, self.y - 45)])
            pygame.draw.polygon(screen, (150, 0, 150), [(self.x + 20, self.y - 40),(self.x + 30, self.y - 60),(self.x + 10, self.y - 45)])
            pygame.draw.arc(screen, (255, 50, 50), [self.x - 20, self.y, 40, 30], math.pi, 2 * math.pi, 3)
        # 血条
        bw, bh = 150, 15
        pygame.draw.rect(screen, (100, 0, 0), (self.x - bw//2, self.y - self.radius - 30, bw, bh))
        pygame.draw.rect(screen, (0, 200, 0), (self.x - bw//2, self.y - self.radius - 30, bw * (self.health / self.max_health), bh))
        pygame.draw.rect(screen, (200, 200, 200), (self.x - bw//2, self.y - self.radius - 30, bw, bh), 2)
        font = pygame.font.SysFont(None, 30)
        boss_level = self._rl.get_boss_level() if self._rl else 1
        name_text = font.render(f"BOSS LV.{boss_level}", True, (255, 100, 255))
        screen.blit(name_text, (self.x - name_text.get_width() // 2, self.y - self.radius - 50))

    def move(self):
        if self.spawn_effect_timer > 0:
            self.spawn_effect_timer -= 1; return
        if self.is_charging:
            nx = self.x + self.charge_direction[0] * self.charge_speed
            ny = self.y + self.charge_direction[1] * self.charge_speed
            if self.radius <= nx <= WIDTH - self.radius and self.radius <= ny <= HEIGHT - self.radius:
                self.x = nx; self.y = ny
            self.charge_timer -= 1
            if self.charge_timer <= 0:
                self.is_charging = False; self.charge_cooldown = 120
        else:
            self.x += self.speed_x; self.y += self.speed_y
            if self.x <= self.radius or self.x >= WIDTH - self.radius: self.speed_x *= -1
            if self.y <= self.radius or self.y >= HEIGHT - self.radius: self.speed_y *= -1
            if random.random() < 0.01: self.speed_x = random.choice([-3, -2, 2, 3])
            if random.random() < 0.01: self.speed_y = random.choice([-3, -2, 2, 3])
            if self.charge_cooldown > 0: self.charge_cooldown -= 1
            if self.charge_cooldown <= 0 and random.random() < 0.02:
                ang = random.uniform(0, 2 * math.pi)
                self.charge_direction = (math.cos(ang), math.sin(ang))
                self.is_charging = True; self.charge_timer = 60

    def update_explosion(self, player, walls):
        if self.explosion_cooldown > 0:
            self.explosion_cooldown -= 1; return False
        self.explosion_cooldown = self.explosion_timer; return True
    
    def create_explosion(self):
        # 依据风险放大爆炸
        r_bonus = getattr(self._rl, 'boss_explosion_radius_bonus', 0) if self._rl else 0
        d_bonus = getattr(self._rl, 'boss_explosion_damage_bonus', 0) if self._rl else 0
        return {"x": self.x, "y": self.y, "radius": 10, "max_radius": 180 + r_bonus, "damage": 20 + d_bonus, "damaged_player": False}

    def take_damage(self, amount, source=None):
        if source != "grenade" and random.random() < self.immune_chance:
            return False
        self.health -= amount; self.flash = 5; return True

    def collide_with_player(self, player):
        return math.hypot(self.x - player.x, self.y - player.y) < self.radius + player.radius

    def collision_damage(self, player):
        player.take_damage(20 if self.is_charging else 10)
        self.speed_x *= -1; self.speed_y *= -1; self.collision_cooldown = 30

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.x = x; self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.life = random.randint(20, 40)
        self.rect = pygame.Rect(self.x, self.y, 1, 1)

    def update(self):
        self.x += self.speed_x; self.y += self.speed_y
        self.life -= 1; self.size = max(0, self.size - 0.1)
        if self.life <= 0:
            self.kill()
            _recycle_particle(self)
            return False
        return True

    def draw(self):
        if self.color == GRENADE_EXPLOSION_COLOR:
            pygame.draw.circle(screen, (255, 200, 100, min(255, self.life*6)), (int(self.x), int(self.y)), int(self.size))
            pygame.draw.circle(screen, (255, 150, 50, min(255, self.life*3)), (int(self.x), int(self.y)), max(1, int(self.size * 1.5)), 1)
        else:
            alpha = min(255, int(self.life * 6))
            pygame.draw.circle(screen, (*self.color, alpha), (int(self.x), int(self.y)), int(self.size))

class FloatingText(pygame.sprite.Sprite):
    def __init__(self, x, y, text, color=(255, 255, 255)):
        super().__init__()
        self.x = x; self.y = y
        self.text = str(text)
        self.color = color
        self.alpha = 255
        self.vy = -1.0
        self.life = 40
        self.rect = pygame.Rect(int(self.x), int(self.y), 1, 1)

    def update(self):
        self.y += self.vy
        self.life -= 1
        self.alpha = max(0, int(255 * (self.life / 40)))
        if self.life <= 0:
            self.kill(); _recycle_float_text(self); return False
        return True

    def draw(self):
        surf = float_font.render(self.text, True, self.color)
        surf.set_alpha(self.alpha)
        screen.blit(surf, (int(self.x - surf.get_width()/2), int(self.y - surf.get_height()/2)))

# 工厂/复用函数
def _get_particle(x, y, color):
    if _PARTICLE_POOL:
        p = _PARTICLE_POOL.pop()
        # 重置属性
        p.x = x; p.y = y; p.color = color
        p.size = random.randint(2, 6)
        p.speed_x = random.uniform(-3, 3)
        p.speed_y = random.uniform(-3, 3)
        p.life = random.randint(20, 40)
        return p
    return Particle(x, y, color)

def _recycle_particle(p):
    try:
        _PARTICLE_POOL.append(p)
    except:
        pass

def _get_float_text(x, y, text, color):
    if _FLOAT_TEXT_POOL:
        ft = _FLOAT_TEXT_POOL.pop()
        ft.x = x; ft.y = y; ft.text = str(text); ft.color = color
        ft.alpha = 255; ft.vy = -1.0; ft.life = 40
        return ft
    return FloatingText(x, y, text, color)

def _recycle_float_text(ft):
    try:
        _FLOAT_TEXT_POOL.append(ft)
    except:
        pass

def _play_explosion_sound():
    global _EXPLOSION_SND_NEXT_TICK
    now = pygame.time.get_ticks()
    if now >= _EXPLOSION_SND_NEXT_TICK:
        explosion_sound.play()
        _EXPLOSION_SND_NEXT_TICK = now + 80  # 最小间隔 80ms

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)
        self.color = WALL_COLOR
        self.border_color = (80, 80, 100)

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)

    def block_bullet(self, bullet):
        return random.random() < 0.3

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x; self.y = y
        self.radius = 12
        self.type = random.choice(["health", "shield", "points"])
        self.timer = 300
        self.float_offset = random.uniform(0, math.pi*2)
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)

    def draw(self):
        fy = self.y + math.sin(pygame.time.get_ticks()/200 + self.float_offset) * 5
        color = (0, 200, 0) if self.type == "health" else ((100, 200, 255) if self.type == "shield" else (255, 215, 0))
        pygame.draw.circle(screen, color, (self.x, fy), self.radius)
        pygame.draw.circle(screen, (200, 200, 200), (self.x, fy), self.radius, 2)
        pulse = abs(math.sin(pygame.time.get_ticks()/200)) * 2
        pygame.draw.circle(screen, (*color, 50), (self.x, fy), int(self.radius + pulse))
        if self.type == "health":
            pygame.draw.rect(screen, (255, 255, 255), (self.x - 4, fy - 8, 8, 16))
            pygame.draw.polygon(screen, (255, 255, 255), [(self.x, fy - 10), (self.x - 6, fy + 2), (self.x + 6, fy + 2)])
        elif self.type == "shield":
            pygame.draw.circle(screen, (255, 255, 255), (self.x, fy), 6, 2)
        else:
            pygame.draw.circle(screen, (255, 255, 255), (self.x, fy), 6)

    def update(self):
        self.timer -= 1; return self.timer > 0

    def collide_with_player(self, player):
        return math.hypot(self.x - player.x, self.y - player.y) < self.radius + player.radius

# 暂停菜单
class PauseMenu:
    def __init__(self):
        self.visible = False
        self.continue_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 60)
        self.quit_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60)

    def draw(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        menu_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 100, 300, 250)
        pygame.draw.rect(screen, (40, 40, 80), menu_rect, border_radius=15)
        pygame.draw.rect(screen, (80, 80, 120), menu_rect, 3, border_radius=15)

        title = FONT_48.render("PAUSED", True, (255, 215, 0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 130))

        mouse_pos = pygame.mouse.get_pos()
        cont_hover = self.continue_button.collidepoint(mouse_pos)
        quit_hover = self.quit_button.collidepoint(mouse_pos)

        cont_color = (100, 200, 100) if cont_hover else (70, 160, 70)
        pygame.draw.rect(screen, cont_color, self.continue_button, border_radius=10)
        pygame.draw.rect(screen, (150, 250, 150), self.continue_button, 3, border_radius=10)
        cont_text = FONT_36.render("CONTINUE", True, (255, 255, 255))
        screen.blit(cont_text, (self.continue_button.centerx - cont_text.get_width()//2, self.continue_button.centery - cont_text.get_height()//2))

        quit_color = (200, 100, 100) if quit_hover else (160, 70, 70)
        pygame.draw.rect(screen, quit_color, self.quit_button, border_radius=10)
        pygame.draw.rect(screen, (250, 150, 150), self.quit_button, 3, border_radius=10)
        quit_text = FONT_36.render("QUIT", True, (255, 255, 255))
        screen.blit(quit_text, (self.quit_button.centerx - quit_text.get_width()//2, self.quit_button.centery - quit_text.get_height()//2))

        info_text = FONT_24.render("Progress saved automatically", True, (180, 180, 200))
        screen.blit(info_text, (WIDTH//2 - info_text.get_width()//2, HEIGHT//2 + 120))

    def handle_event(self, event, player, enemies, score):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.continue_button.collidepoint(event.pos):
                self.visible = False; return True
            if self.quit_button.collidepoint(event.pos):
                GameData.save_game_state({
                    "player": {
                        "x": player.x, "y": player.y, "health": player.health,
                        "shield": player.shield, "weapon": player.weapon, "score": player.score,
                        "attack_boost_active": player.attack_boost_active,
                        "attack_boost_duration": player.attack_boost_duration,
                        "attack_boost_cooldown": player.attack_boost_cooldown,
                        "grenade_cooldown": player.grenade_cooldown,
                        "fire_binding": getattr(player, 'fire_binding', 'space')
                    },
                    "enemies": [{"x": e.x, "y": e.y, "health": e.health} for e in enemies],
                    "score": score
                })
                return False
        return True

# 奖励菜单（通关后选一）
class RewardMenu:
    def __init__(self):
        self.visible = False
        self.options = []  # [(name, apply_fn)]

    def build_options(self, player):
        self.options = [
            ("+20 Shield Max", lambda p: setattr(p, 'shield_max', p.shield_max + 20)),
            ("+0.5 Move Speed", lambda p: setattr(p, 'speed', p.speed + 0.5)),
            ("+2 Bullet Damage", lambda p: setattr(p, 'bullet_damage', p.bullet_damage + 2)),
        ]
        random.shuffle(self.options)
        self.options = self.options[:3]

    def draw(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200)); screen.blit(overlay, (0, 0))
        panel = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 150, 500, 320)
        pygame.draw.rect(screen, (40, 60, 90), panel, border_radius=12)
        pygame.draw.rect(screen, (100, 150, 220), panel, 3, border_radius=12)
        title = FONT_48.render("CHOOSE ONE", True, (255, 215, 0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, panel.top + 20))
        small = FONT_28
        hint = small.render("Press 1 / 2 / 3 to pick", True, (220, 220, 240))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, panel.bottom - 40))
        for i, (name, _) in enumerate(self.options):
            box = pygame.Rect(panel.left + 30, panel.top + 80 + i*70, 440, 50)
            pygame.draw.rect(screen, (60, 80, 110), box, border_radius=8)
            pygame.draw.rect(screen, (120, 170, 240), box, 2, border_radius=8)
            label = FONT_36.render(f"{i+1}. {name}", True, (255, 255, 255))
            screen.blit(label, (box.left + 12, box.top + 10))
        
    def handle_event(self, event, player, rl_manager=None, was_boss_battle=False):
        if event.type == pygame.KEYDOWN:
            idx = None
            if event.key == pygame.K_1: idx = 0
            elif event.key == pygame.K_2: idx = 1
            elif event.key == pygame.K_3: idx = 2
            if idx is not None and 0 <= idx < len(self.options):
                try:
                    self.options[idx][1](player)
                except:
                    pass
                
                # 如果是BOSS战胜利，应用永久加成
                boss_bonus_info = None
                if was_boss_battle and rl_manager:
                    boss_bonus_info = rl_manager.apply_boss_victory_bonus(player)
                
                # 推进到下一房间/层
                end_of_floor = False
                if rl_manager:
                    # 在推进前判断是否处于层末尾
                    end_of_floor = (rl_manager.room >= rl_manager.rooms_per_floor)
                    rl_manager.advance()
                
                self.visible = False
                return True, boss_bonus_info, end_of_floor
        return False, None, False


class ShopMenu:
    def __init__(self):
        self.visible = False
        self.items = []  # [{'name':..., 'price':..., 'apply': fn, 'purchased': False}]
        self.next_btn = pygame.Rect(0,0,0,0)

    def build_options(self, player):
        candidates = [
            { 'name': '+30 HP (Heal)', 'price': 20, 'apply': lambda p: setattr(p, 'health', min(p.max_health, p.health + 30)) },
            { 'name': '+20 Shield Max', 'price': 25, 'apply': lambda p: setattr(p, 'shield_max', p.shield_max + 20) },
            { 'name': '+5 Bullet Damage', 'price': 40, 'apply': lambda p: setattr(p, 'bullet_damage', p.bullet_damage + 5) },
            { 'name': '+10 Grenade Damage', 'price': 35, 'apply': lambda p: None },  # 真正加成为 rl 的永久加成，由主循环应用
            { 'name': '+0.5 Move Speed', 'price': 30, 'apply': lambda p: setattr(p, 'speed', p.speed + 0.5) },
        ]
        random.shuffle(candidates)
        # 取前三项
        self.items = []
        for it in candidates[:3]:
            self.items.append({ **it, 'purchased': False })

    def draw(self, player):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200)); screen.blit(overlay, (0, 0))

        panel = pygame.Rect(WIDTH//2 - 280, HEIGHT//2 - 200, 560, 380)
        pygame.draw.rect(screen, (40, 60, 90), panel, border_radius=12)
        pygame.draw.rect(screen, (120, 170, 240), panel, 3, border_radius=12)
        title = FONT_48.render("SHOP", True, (255, 215, 0))
        screen.blit(title, (panel.centerx - title.get_width()//2, panel.top + 16))

        # Gold 显示
        small = FONT_28
        gold_text = small.render(f"Gold: {player.gold}", True, (255, 215, 0))
        screen.blit(gold_text, (panel.left + 20, panel.top + 18))

        # 商品列表
        item_font = FONT_30
        for i, it in enumerate(self.items):
            box = pygame.Rect(panel.left + 26, panel.top + 70 + i*80, panel.width - 52, 60)
            pygame.draw.rect(screen, (60, 80, 110), box, border_radius=10)
            pygame.draw.rect(screen, (120, 170, 240), box, 2, border_radius=10)
            label = item_font.render(f"{i+1}. {it['name']}  -  {it['price']}g", True, (255, 255, 255))
            screen.blit(label, (box.left + 14, box.top + 16))
            # 购买状态
            status = "Purchased" if it['purchased'] else ("Buy" if player.gold >= it['price'] else "Need Gold")
            color = (120, 220, 140) if not it['purchased'] and player.gold >= it['price'] else ((180,180,180) if it['purchased'] else (220,120,120))
            st = small.render(status, True, color)
            screen.blit(st, (box.right - st.get_width() - 12, box.top + 18))

        # 下一层按钮
        self.next_btn = pygame.Rect(panel.centerx - 120, panel.bottom - 60, 240, 44)
        pygame.draw.rect(screen, (60, 150, 90), self.next_btn, border_radius=10)
        pygame.draw.rect(screen, (90, 200, 130), self.next_btn, 2, border_radius=10)
        nlabel = FONT_32.render("NEXT FLOOR", True, (255, 255, 255))
        screen.blit(nlabel, (self.next_btn.centerx - nlabel.get_width()//2, self.next_btn.centery - nlabel.get_height()//2))

    def handle_event(self, event, player, rl_manager=None):
        # 返回 (consumed, proceed_next)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.next_btn.collidepoint(pygame.mouse.get_pos()):
                self.visible = False
                return True, True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                self.visible = False
                return True, True
            idx = None
            if event.key == pygame.K_1: idx = 0
            elif event.key == pygame.K_2: idx = 1
            elif event.key == pygame.K_3: idx = 2
            if idx is not None and 0 <= idx < len(self.items):
                it = self.items[idx]
                if not it['purchased'] and player.gold >= it['price']:
                    if it['name'].startswith('+10 Grenade Damage') and rl_manager is not None:
                        # 特殊：手雷伤害加成归入永久加成池
                        rl_manager.player_permanent_bonuses['grenade_damage_bonus'] += 10
                    ok = player.spend_gold(it['price'])
                    if ok:
                        try:
                            it['apply'](player)
                        except:
                            pass
                        it['purchased'] = True
                        return True, False
        return False, False

# Roguelike 地城管理
class RoguelikeManager:
    def __init__(self, difficulty="Normal"):
        self.floor = 1
        self.room = 1
        self.rooms_per_floor = 4
        self.max_floors = 15  # 总共15层
        self.spawn_interval = 90
        self.target_enemies = 6
        self.spawned = 0
        self.timer = 0
        self.cap = 6
        self.diff = difficulty
        # 难度参数
        self.cap_base_offset = 0
        self.base_enemies_offset = 0
        self.enemy_scale_bonus = 0.0
        self.apply_difficulty()
        # 集成战略风格的风险(Risk)系统：0..20
        self.risk = 0
        # 风险调度：每进入新房间时依据风险提高各种系数
        self.enemy_health_mult = 1.0
        self.enemy_speed_mult = 1.0
        self.player_damage_mult = 1.0
        self.boss_health_mult = 1.0
        self.boss_immune_bonus = 0.0
        self.boss_explosion_radius_bonus = 0
        self.boss_explosion_damage_bonus = 0
        # 玩家属性增强记录
        self.player_permanent_bonuses = {
            'health_bonus': 0,
            'damage_bonus': 0,
            'grenade_damage_bonus': 0,
            'speed_bonus': 0
        }

    def difficulty_scale(self):
        return 1.0 + (self.floor - 1) * 0.25 + (self.room - 1) * 0.1

    def apply_difficulty(self):
        # 基础 spawn_interval=90，简单更慢，困难更快
        if self.diff == "Easy":
            self.spawn_interval = 110
            self.cap_base_offset = -2
            self.base_enemies_offset = -2
            self.enemy_scale_bonus = -0.1
        elif self.diff == "Hard":
            self.spawn_interval = 70
            self.cap_base_offset = +2
            self.base_enemies_offset = +2
            self.enemy_scale_bonus = +0.2
        else:
            self.spawn_interval = 90
            self.cap_base_offset = 0
            self.base_enemies_offset = 0
            self.enemy_scale_bonus = 0.0

    def gen_walls(self):
        walls = pygame.sprite.Group()
        # 基于房间生成一些不重叠的平台/墙
        count = 5 + (self.room % 3)
        min_w, max_w = 80, 180
        min_h, max_h = 16, 28
        margin = 40
        gap = 12  # 墙体之间的最小间隔
        rects = []
        for _ in range(count):
            placed = False
            for _try in range(200):
                w = random.randint(min_w, max_w); h = random.randint(min_h, max_h)
                x = random.randint(margin, WIDTH - w - margin)
                y = random.randint(80, HEIGHT - h - 120)
                r = pygame.Rect(x, y, w, h)
                # 要求与已放置墙体保持 gap 间隔
                inflated = r.inflate(gap, gap)
                if any(inflated.colliderect(orect) for orect in rects):
                    continue
                rects.append(r)
                walls.add(Wall(x, y, w, h))
                placed = True
                break
            if not placed:
                # 兜底：若实在放不下，放置一个小平台到安全区域
                w = 100; h = 20; x = margin; y = 120
                rects.append(pygame.Rect(x, y, w, h))
                walls.add(Wall(x, y, w, h))
        return walls

    def start_room(self, enemies, walls, boss_warning_timer_ref=None):
        self.spawned = 0
        self.timer = 0
        self.cap = max(3, 5 + self.room + self.cap_base_offset)
        base = max(3, 6 + (self.floor - 1) * 2 + self.base_enemies_offset)
        self.target_enemies = base + random.randint(0, 3)
        
        # 检查是否需要生成BOSS（第5层开始，每5层的第4个房间）
        if self.is_boss_floor() and self.room == 4 and boss_warning_timer_ref is not None:
            # 设置BOSS警告计时器
            boss_warning_timer_ref[0] = 180  # 3秒警告时间
            self.target_enemies = 0  # BOSS房间不生成普通敌人
        
        # 进入新房间时提升风险（若为固定Risk模式则不再自动增加）
        if not getattr(self, 'risk_fixed', False):
            inc = 1 if self.diff == "Easy" else (2 if self.diff == "Normal" else 3)
            self.risk = min(20, self.risk + inc)
        self.apply_risk_modifiers()
        # 生成新房间墙体
        walls.empty()
        nw = self.gen_walls()
        for w in nw:
            walls.add(w)
        enemies.empty()
        # 将玩家放置到安全位置，避免卡墙
        if hasattr(self, 'player') and self.player is not None:
            player = self.player
            safe_pos_found = False
            for _ in range(120):
                px = random.randint(player.radius + 10, WIDTH - player.radius - 10)
                py = random.randint(HEIGHT//2, HEIGHT - player.radius - 10)
                prect = pygame.Rect(px - player.radius, py - player.radius, player.radius*2, player.radius*2)
                if not any(prect.colliderect(w.rect) for w in walls):
                    player.x = px; player.y = py
                    player.rect.topleft = (player.x - player.radius, player.y - player.radius)
                    safe_pos_found = True
                    break
            if not safe_pos_found:
                # 兜底：左下角安全区
                player.x = player.radius + 20
                player.y = HEIGHT - player.radius - 20
                player.rect.topleft = (player.x - player.radius, player.y - player.radius)

    def update_spawning(self, enemies, walls):
        self.timer += 1
        if self.spawned < self.target_enemies and len(enemies) < self.cap and self.timer >= self.spawn_interval:
            e = spawn_random_enemy(walls, self)
            # 提升难度：生命值/速度
            sc = self.difficulty_scale() + self.enemy_scale_bonus
            # 敌人受风险影响
            sc *= self.enemy_health_mult
            e.max_health = int(e.max_health * sc)
            e.health = e.max_health
            e.speed = min(3.5, e.speed * (1.0 + (sc - 1) * 0.5) * self.enemy_speed_mult)
            enemies.add(e)
            self.spawned += 1
            self.timer = 0

    def room_cleared(self, enemies, boss):
        return self.spawned >= self.target_enemies and len(enemies) == 0 and not boss

    def is_boss_floor(self):
        """判断当前楼层是否应该出现BOSS（第5层开始，每5层一次）"""
        return self.floor >= 5 and self.floor % 5 == 0
    
    def is_final_floor(self):
        """判断是否到达最终层"""
        return self.floor >= self.max_floors
    
    def get_boss_level(self):
        """获取BOSS等级（用于属性增强）"""
        if not self.is_boss_floor():
            return 0
        return (self.floor // 5)
    
    def apply_boss_victory_bonus(self, player):
        """BOSS战胜利后给予玩家永久加成"""
        boss_level = self.get_boss_level()
        if boss_level > 0:
            # 生命值加成（每个BOSS +20最大生命值）
            health_bonus = 20
            self.player_permanent_bonuses['health_bonus'] += health_bonus
            player.max_health += health_bonus
            player.health = min(player.max_health, player.health + health_bonus)  # 也回复一些血量
            
            # 伤害加成（每个BOSS +10%伤害）
            damage_bonus = 0.1
            self.player_permanent_bonuses['damage_bonus'] += damage_bonus
            
            # 手雷伤害加成（每个BOSS +15伤害）
            grenade_bonus = 15
            self.player_permanent_bonuses['grenade_damage_bonus'] += grenade_bonus
            
            # 速度轻微加成（每个BOSS +0.2速度）
            speed_bonus = 0.2
            self.player_permanent_bonuses['speed_bonus'] += speed_bonus
            player.speed += speed_bonus
            
            return {
                'health': health_bonus,
                'damage': int(damage_bonus * 100),
                'grenade': grenade_bonus,
                'speed': speed_bonus
            }
        return None

    def advance(self):
        self.room += 1
        if self.room > self.rooms_per_floor:
            if self.floor < self.max_floors:  # 只有未达到最大层数才继续
                self.floor += 1
                self.room = 1
                # 每层完成后增加手雷伤害
                self.player_permanent_bonuses['grenade_damage_bonus'] += 5
    
    def apply_risk_modifiers(self):
        # 将 risk 线性映射到不同的效果（0..20）
        		# 注意：本文件使用制表符缩进；以下行需缩进到方法体
        r = self.risk
        extra = max(0, r - 12)  # 从12级开始加速
        # 敌人强化（整体稍增，12级后增速加快）
        self.enemy_health_mult = 1.0 + 0.02 * r + 0.01 * extra       # ~+48% at 20
        self.enemy_speed_mult  = 1.0 + 0.01 * r + 0.005 * extra      # ~+24% at 20
        # 玩家削弱（整体稍增，12级后加速，最低0.6）
        self.player_damage_mult = max(0.6, 1.0 - (0.01 * r + 0.005 * extra))
        # Boss 强化（整体稍增，12级后增速加快）
        self.boss_health_mult   = 1.0 + 0.03 * r + 0.015 * extra     # ~+72% at 20
        self.boss_immune_bonus  = min(0.5, 0.02 * r + 0.005 * extra) # 封顶提高到0.5
        self.boss_explosion_radius_bonus = int(2 * r + 1 * extra)    # ~48px at 20
        self.boss_explosion_damage_bonus = int(1 * r + 0.5 * extra)  # ~24 dmg at 20

# 绘制
def draw_background():
    screen.fill(BACKGROUND)
    for i in range(100):
        x = (i * 37) % WIDTH; y = (i * 23) % HEIGHT
        size = random.randint(1, 2); b = random.randint(100, 200)
        pygame.draw.circle(screen, (b, b, 255), (x, y), size)
    t = pygame.time.get_ticks() / 1000
    for i in range(5):
        sp = 0.5 + i * 0.2
        x = (t * sp * 50) % WIDTH; y = (t * sp * 30 + i * 100) % HEIGHT
        for j in range(10):
            px = x - j * 3; py = y - j * 1.5; alpha = max(0, 255 - j * 25)
            size = max(1, int(3 - j * 0.3))
            pygame.draw.circle(screen, (200, 200, 255, alpha), (int(px), int(py)), size)

def draw_health_bar(player, x, y, w, h):
    pygame.draw.rect(screen, (50, 50, 80), (x, y, w, h))
    hw = w * (player.health / 100)
    for i in range(int(hw)):
        color_value = int(200 * (i / max(1, hw)))
        pygame.draw.line(screen, (color_value, 200 - color_value//2, 50), (x + i, y), (x + i, y + h))
    pygame.draw.rect(screen, (150, 150, 200), (x, y, w, h), 2)
    small_font = FONT_24
    screen.blit(small_font.render(f"{player.health}%", True, TEXT_COLOR), (x + w + 10, y))
    sh_h = h // 2; sh_y = y + h + 5
    pygame.draw.rect(screen, (30, 30, 60), (x, sh_y, w, sh_h))
    if player.shield > 0:
        sw = w * (player.shield / player.shield_max)
        for i in range(int(sw)):
            bv = min(255, 150 + int(100 * (i / max(1, sw))))
            pygame.draw.line(screen, (50, 150, bv), (x + i, sh_y), (x + i, sh_y + sh_h))
    pygame.draw.rect(screen, (100, 150, 255), (x, sh_y, w, sh_h), 2)
    screen.blit(small_font.render(f"Shield: {player.shield:.0f}/{player.shield_max}", True, (100, 200, 255)), (x + w + 10, sh_y))

def draw_weapon_indicator(x, y, weapon_index):
    colors = [PLAYER_BULLET_COLOR, SHOTGUN_COLOR, GRENADE_COLOR]
    pygame.draw.rect(screen, (40, 40, 60), (x, y, 120, 40), border_radius=5)
    for i in range(3):
        icon = pygame.Rect(x + 10 + i*40, y + 5, 30, 30)
        if i == weapon_index:
            pygame.draw.rect(screen, (80, 80, 120), icon, border_radius=5)
            pygame.draw.rect(screen, colors[i], icon, 2, border_radius=5)
            pulse = abs(math.sin(pygame.time.get_ticks()/200)) * 10
            pygame.draw.rect(screen, (*colors[i], 50), pygame.Rect(x + 5 + i*40, y, 40, 40), border_radius=8)
        else:
            pygame.draw.rect(screen, (60, 60, 80), icon, border_radius=5)
        if i == 0: pygame.draw.rect(screen, colors[i], (x+15+i*40, y+15, 20, 8))
        elif i == 1:
            pygame.draw.rect(screen, colors[i], (x+15+i*40, y+15, 10, 8))
            pygame.draw.rect(screen, colors[i], (x+25+i*40, y+12, 5, 14))
        else:
            pygame.draw.circle(screen, colors[i], (x+25+i*40, y+20), 8)

def draw_ui_panel(player):
    ui_surf = pygame.Surface((WIDTH, 80), pygame.SRCALPHA); ui_surf.fill(UI_BG)
    screen.blit(ui_surf, (0, HEIGHT - 80))
    font = FONT_36; small_font = FONT_24
    screen.blit(font.render(f"Weapon: {player.weapon_names[player.weapon]}", True, TEXT_COLOR), (20, HEIGHT - 70))
    screen.blit(small_font.render("Press 1,2,3 to switch weapons", True, (180, 180, 180)), (20, HEIGHT - 35))
    skill_name = {
        None: "No Skill",
        'rapid': 'Rapid Fire',
        'fortify': 'Fortify',
        'triple': 'Triple Buckshot',
    }.get(getattr(player, 'selected_skill', None), 'Skill')
    screen.blit(small_font.render(f"Press F: {skill_name}", True, (200, 200, 100)), (450, HEIGHT - 35))
    input_warning = small_font.render("(Use Eng.input!)", True, (255, 100, 100))
    screen.blit(input_warning, (WIDTH - input_warning.get_width() - 20, HEIGHT - 35))
    # 技能冷却统一显示（rapid 使用 attack_boost_*，其余使用 skill_cooldown）
    pygame.draw.rect(screen, (50, 50, 80), (450, HEIGHT - 65, 200, 20))
    cd_ratio = 1.0; cd_text = "Ready"
    if getattr(player, 'selected_skill', None) == 'rapid':
        if player.attack_boost_cooldown > 0:
            cd_ratio = 1 - (player.attack_boost_cooldown / 900)
            cd_text = f"CD: {player.attack_boost_cooldown//60+1}s"
        elif player.attack_boost_active:
            cd_text = "ACTIVE"
    elif getattr(player, 'selected_skill', None) in ('fortify','triple'):
        if player.skill_cooldown > 0:
            cd_ratio = 1 - (player.skill_cooldown / 900)
            cd_text = f"CD: {player.skill_cooldown//60+1}s"
    pygame.draw.rect(screen, (255, 200, 0), (450, HEIGHT - 65, int(200 * cd_ratio), 20))
    pygame.draw.rect(screen, (150, 150, 50), (450, HEIGHT - 65, 200, 20), 2)
    screen.blit(small_font.render(cd_text, True, TEXT_COLOR), (455, HEIGHT - 65))
    if player.weapon == 2:
        pygame.draw.rect(screen, (50, 50, 80), (250, HEIGHT - 65, 150, 20))
        if player.grenade_cooldown > 0:
            cp = 1 - (player.grenade_cooldown / 600)
            pygame.draw.rect(screen, (100, 255, 100), (250, HEIGHT - 65, int(150 * cp), 20))
        else:
            pygame.draw.rect(screen, (100, 255, 100), (250, HEIGHT - 65, 150, 20))
        pygame.draw.rect(screen, (50, 150, 50), (250, HEIGHT - 65, 150, 20), 2)
        gt = small_font.render((f"Grenade CD: {player.grenade_cooldown//60+1}s" if player.grenade_cooldown>0 else "Grenade Ready"), True, TEXT_COLOR)
        screen.blit(gt, (255, HEIGHT - 65))

# 工具
def create_explosion(particles, x, y, size=1.0):
    use_add = hasattr(particles, 'add')
    for _ in range(int(30 * size)):
        (particles.add if use_add else particles.append)(_get_particle(x, y, (255, 220, 100)))
    for _ in range(int(20 * size)):
        (particles.add if use_add else particles.append)(_get_particle(x, y, (255, 100, 50)))
    for _ in range(int(10 * size)):
        (particles.add if use_add else particles.append)(_get_particle(x, y, (150, 150, 150)))
    for i in range(5):
        radius = i * 15; alpha = 200 - i * 40
        pygame.draw.circle(screen, (255, 200, 100, alpha), (x, y), radius, 2)
    _play_explosion_sound()

def spawn_floating_text(particles, x, y, text, color):
    try:
        ft = _get_float_text(x, y, text, color)
        if hasattr(particles, 'add'):
            particles.add(ft)
        else:
            particles.append(ft)
    except:
        pass

# 开局技能选择菜单（一次性）
class SkillSelectMenu:
    def __init__(self):
        self.visible = True
        self.options = [
            ("Rapid Fire", 'rapid', "Attack speed up for 5s. CD 15s"),
            ("Fortify", 'fortify', "+40 Shield and Heal 40. CD 15s"),
            ("Triple Buckshot", 'triple', "Fire 3 shotgun volleys instantly. CD 15s"),
        ]
        self.selected = 0

    def draw(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        title = FONT_48.render("Choose a Skill", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 180))
        for i, (name, _, desc) in enumerate(self.options):
            y = HEIGHT//2 - 60 + i*60
            color = (255, 255, 0) if i == self.selected else (220, 220, 220)
            text = FONT_36.render(f"{i+1}. {name}", True, color)
            screen.blit(text, (WIDTH//2 - 220, y))
            d = FONT_24.render(desc, True, (200, 200, 200))
            screen.blit(d, (WIDTH//2 - 220, y + 32))
        hint = FONT_24.render("Press 1/2/3 or Enter to confirm", True, (200, 200, 200))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 140))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_KP1): self.selected = 0; return None
            if event.key in (pygame.K_2, pygame.K_KP2): self.selected = 1; return None
            if event.key in (pygame.K_3, pygame.K_KP3): self.selected = 2; return None
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.visible = False
                return self.options[self.selected][1]
        return None

# 控制方式选择菜单
class ControlSelectMenu:
    def __init__(self):
        self.visible = True
        # 0: 空格开火；1: 鼠标左键开火
        self.options = [
            ("Space to Fire", 'space', "Press SPACE to shoot (default)"),
            ("Left Mouse to Fire", 'mouse', "Click LMB to shoot")
        ]
        self.selected = 0

    def draw(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        title = FONT_48.render("Choose Controls", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 180))
        for i, (name, _, desc) in enumerate(self.options):
            y = HEIGHT//2 - 60 + i*60
            color = (255, 255, 0) if i == self.selected else (220, 220, 220)
            text = FONT_36.render(f"{i+1}. {name}", True, color)
            screen.blit(text, (WIDTH//2 - 220, y))
            d = FONT_24.render(desc, True, (200, 200, 200))
            screen.blit(d, (WIDTH//2 - 220, y + 32))
        hint = FONT_24.render("Press 1/2 or Enter to confirm", True, (200, 200, 200))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 140))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_KP1): self.selected = 0; return None
            if event.key in (pygame.K_2, pygame.K_KP2): self.selected = 1; return None
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.visible = False
                return self.options[self.selected][1]
        return None

# 入口
def show_victory_screen(player, rl_manager):
    """显示游戏胜利界面"""
    # 触发游戏完成成就
    achievement_system.update_progress("game_complete", 1)
    
    font = FONT_48
    small_font = FONT_36
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
        
        draw_background()
        
        # 胜利文本
        victory_text = font.render("CONGRATULATIONS!", True, (255, 215, 0))
        screen.blit(victory_text, (WIDTH//2 - victory_text.get_width()//2, HEIGHT//2 - 150))
        
        complete_text = small_font.render("You have conquered all 15 floors!", True, (150, 255, 150))
        screen.blit(complete_text, (WIDTH//2 - complete_text.get_width()//2, HEIGHT//2 - 100))
        
        score_text = small_font.render(f"Final Score: {player.score}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 50))
        
        bosses_defeated = len([f for f in range(5, 16, 5) if f <= rl_manager.floor])
        boss_text = small_font.render(f"Bosses Defeated: {bosses_defeated}/3", True, (255, 180, 255))
        screen.blit(boss_text, (WIDTH//2 - boss_text.get_width()//2, HEIGHT//2))
        
        bonuses = rl_manager.player_permanent_bonuses
        bonus_text = small_font.render(f"Permanent Bonuses: +{bonuses['health_bonus']} HP, +{int(bonuses['damage_bonus']*100)}% DMG, +{bonuses['grenade_damage_bonus']} Grenade", True, (200, 200, 255))
        screen.blit(bonus_text, (WIDTH//2 - bonus_text.get_width()//2, HEIGHT//2 + 50))
        
        continue_text = small_font.render("Press R to return to menu", True, (200, 200, 200))
        screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 100))
        
        pygame.display.flip()
        pygame.time.delay(30)


def main(load_saved_state=False, difficulty="Normal"):
    prev_hkl = get_current_input_method()
    set_input_method_to_english()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)

    player = Player()
    # 开局技能选择（仅首次进入）
    skill_menu = SkillSelectMenu()
    chosen = None
    while skill_menu.visible:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                restore_input_method(prev_hkl); pygame.quit(); sys.exit()
            res = skill_menu.handle_event(event)
            if res is not None:
                chosen = res
        draw_background()
        skill_menu.draw()
        pygame.display.flip(); clock.tick(60)
    player.selected_skill = chosen or 'rapid'
    # 控制方式选择
    ctrl_menu = ControlSelectMenu()
    chosen_ctrl = None
    while ctrl_menu.visible:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                restore_input_method(prev_hkl); pygame.quit(); sys.exit()
            res = ctrl_menu.handle_event(event)
            if res is not None:
                chosen_ctrl = res
        draw_background()
        ctrl_menu.draw()
        pygame.display.flip(); clock.tick(60)
    player.fire_binding = chosen_ctrl or 'space'
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    grenades = pygame.sprite.Group()
    particles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    walls = pygame.sprite.Group()
    for w in [
        Wall(100, 200, 80, 20), Wall(300, 150, 20, 100), Wall(500, 250, 120, 20),
        Wall(200, 400, 20, 80), Wall(600, 350, 80, 20), Wall(150, 500, 200, 20), Wall(450, 100, 20, 80)
    ]:
        walls.add(w)

    enemies = pygame.sprite.Group()
    for _ in range(5):
        enemies.add(Enemy(walls))

    boss = None; boss_explosions = []; boss_warning_timer = [0]; boss_spawned = False

    game_over = False
    record_saved = False
    powerup_timer = 0
    shake_time = 0; shake_intensity = 0; shake_offset = (0, 0)
    enemy_kills = 0
    player_died_from_explosion = False
    player_died_from_collision = False
    
    pause_menu = PauseMenu()
    reward_menu = RewardMenu()
    shop_menu = ShopMenu()
    # 支持两种模式：
    # 1) 传统 Easy/Normal/Hard（每房间自动增加风险）
    # 2) Risk 模式（以固定 Risk 等级开始，不自动增加）
    if isinstance(difficulty, dict) and difficulty.get('type') == 'risk':
        rl = RoguelikeManager("Normal")
        rl.risk = max(0, min(20, int(difficulty.get('value', 0))))
        rl.risk_fixed = True
        rl.apply_risk_modifiers()
    else:
        rl = RoguelikeManager(difficulty)
    # 让 Roguelike 管理器可以在换房间时重定位玩家
    rl.player = player

    if load_saved_state:
        saved = GameData.load_game_state()
        if saved:
            p = saved.get("player", {})
            player.x = p.get("x", player.x); player.y = p.get("y", player.y)
            player.health = p.get("health", player.health)
            player.shield = p.get("shield", player.shield)
            player.weapon = p.get("weapon", player.weapon)
            player.score = p.get("score", player.score)
            player.attack_boost_active = p.get("attack_boost_active", False)
            player.attack_boost_duration = p.get("attack_boost_duration", 0)
            player.attack_boost_cooldown = p.get("attack_boost_cooldown", 0)
            player.grenade_cooldown = p.get("grenade_cooldown", 0)
            player.fire_binding = p.get("fire_binding", getattr(player, 'fire_binding', 'space'))
            enemies.empty()
            for ed in saved.get("enemies", []):
                e = Enemy(walls)
                e.x = ed.get("x", e.x)
                e.y = ed.get("y", e.y)
                e.health = ed.get("health", e.health)
                e.rect.topleft = (e.x - e.radius, e.y - e.radius)
                enemies.add(e)

    return_to_menu = False
    # 初始房间生成
    rl.start_room(enemies, walls, boss_warning_timer)
    
    # 添加游戏开始时间记录（用于生存时间成就）
    game_start_time = pygame.time.get_ticks()

    while not return_to_menu:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if pause_menu.visible:
                if not pause_menu.handle_event(event, player, enemies, player.score):
                    return_to_menu = True
                continue
            # 奖励菜单事件
            if reward_menu.visible:
                # 检查是否刚刚击败了BOSS
                was_boss_battle = (boss is None and boss_spawned)
                handled, boss_bonus, end_of_floor = reward_menu.handle_event(event, player, rl, was_boss_battle)
                if handled:
                    # 选择完成，检查游戏状态
                    if boss_bonus:
                        # 显示BOSS胜利奖励信息
                        print(f"BOSS defeated! Bonuses: +{boss_bonus['health']} HP, +{boss_bonus['damage']}% Damage, +{boss_bonus['grenade']} Grenade Damage, +{boss_bonus['speed']} Speed")
                    
                    # 检查是否游戏胜利
                    if rl.is_final_floor() and rl.room > rl.rooms_per_floor:
                        # 游戏胜利！显示胜利界面
                        show_victory_screen(player, rl)
                        return_to_menu = True
                        continue
                    
                    # 重置BOSS状态
                    if was_boss_battle:
                        boss_spawned = False
                    # 层结束则进入商店
                    if end_of_floor:
                        shop_menu.visible = True
                        shop_menu.build_options(player)
                    else:
                        rl.start_room(enemies, walls, boss_warning_timer)
                continue
            # 商店事件
            if shop_menu.visible:
                consumed, proceed_next = shop_menu.handle_event(event, player, rl)
                if consumed:
                    if proceed_next:
                        # 商店结束后开始下一房间/层（RewardMenu 已经 advance 过）
                        rl.start_room(enemies, walls, boss_warning_timer)
                    continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    pause_menu.visible = True
                # 仅当绑定为空格时才响应空格射击
                if event.key == pygame.K_SPACE and not game_over and getattr(player, 'fire_binding', 'space') == 'space':
                    player.shoot(bullets, grenades)
                if event.key == pygame.K_r and game_over:
                    return_to_menu = True; game_over = False
                if not game_over:
                    if event.key == pygame.K_1: player.weapon = 0
                    elif event.key == pygame.K_2: player.weapon = 1
                    elif event.key == pygame.K_3: player.weapon = 2
                    elif event.key == pygame.K_f:
                        if player.activate_selected_skill(bullets):
                            for _ in range(30): particles.add(Particle(player.x, player.y, (255, 200, 0)))
                            skill_activate_sound.play()
            # 鼠标左键开火（仅当绑定为 mouse）
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                if getattr(player, 'fire_binding', 'space') == 'mouse':
                    player.shoot(bullets, grenades)

        if return_to_menu:
            restore_input_method(prev_hkl)
            return

        if pause_menu.visible:
            pause_menu.draw(); pygame.display.flip(); continue
        if reward_menu.visible:
            # 奖励选择时仅显示界面
            draw_background()
            for w in walls: w.draw()
            for e in enemies: e.draw(player)
            player.draw()
            draw_health_bar(player, 150, 25, 200, 20)
            draw_weapon_indicator(20, HEIGHT - 120, player.weapon)
            draw_ui_panel(player)
            reward_menu.draw()
            pygame.display.flip(); clock.tick(60); continue
        if shop_menu.visible:
            # 商店开启时暂停战斗，仅显示商店界面
            draw_background()
            for w in walls: w.draw()
            for e in enemies: e.draw(player)
            player.draw()
            draw_health_bar(player, 150, 25, 200, 20)
            draw_weapon_indicator(20, HEIGHT - 120, player.weapon)
            draw_ui_panel(player)
            shop_menu.draw(player)
            pygame.display.flip(); clock.tick(60); continue

        # Game over
        if game_over:
            draw_background()
            if not record_saved:
                # 保存分数、难度/风险与层数
                diff_label = (difficulty if isinstance(difficulty, str) else (f"Risk {difficulty.get('value', 0)}" if isinstance(difficulty, dict) and difficulty.get('type')=='risk' else 'Normal'))
                GameData.add_record(player.score, difficulty=diff_label, floor=rl.floor)
                
                # 触发成就系统更新
                survival_time = (pygame.time.get_ticks() - game_start_time) / 1000  # 秒
                achievement_system.update_progress("survival_time", survival_time)
                achievement_system.update_progress("score", player.score)
                achievement_system.update_progress("floor", rl.floor)
                if isinstance(difficulty, dict) and difficulty.get('type') == 'risk':
                    achievement_system.update_progress("difficulty", difficulty.get('value', 0))
                elif difficulty == "Hard":
                    achievement_system.update_progress("difficulty", 8)
                elif difficulty == "Normal":
                    achievement_system.update_progress("difficulty", 5)
                else:  # Easy
                    achievement_system.update_progress("difficulty", 3)
                
                record_saved = True
                # 游戏结束后恢复输入法（只需执行一次）
                restore_input_method(prev_hkl)
            death_text = FONT_36.render("WASTED!", True, (255, 50, 50))
            screen.blit(death_text, (WIDTH//2 - death_text.get_width()//2, HEIGHT//2 - 150))
            cause = ("Crushed by enemies" if player_died_from_collision else ("Blown up by grenade" if player_died_from_explosion else "Shot by enemies"))
            screen.blit(FONT_36.render(cause, True, (200, 100, 100)), (WIDTH//2 - FONT_36.size(cause)[0]//2, HEIGHT//2 - 100))
            screen.blit(FONT_36.render("GAME OVER!", True, (255, 50, 50)), (WIDTH//2 - 100, HEIGHT//2 - 40))
            screen.blit(FONT_36.render(f"Final Score: {player.score}", True, TEXT_COLOR), (WIDTH//2 - 120, HEIGHT//2))
            screen.blit(FONT_36.render(f"Floor {rl.floor} - Room {rl.room}", True, TEXT_COLOR), (WIDTH//2 - 120, HEIGHT//2 + 40))
            screen.blit(FONT_36.render("Press R to return to menu", True, TEXT_COLOR), (WIDTH//2 - 180, HEIGHT//2 + 80))
            pygame.display.flip(); clock.tick(60); continue

        # BOSS出现警告
        if boss_warning_timer[0] > 0:
            boss_warning_timer[0] -= 1
            if boss_warning_timer[0] <= 0 and not boss_spawned:
                boss = Boss(rl); boss_spawned = True; boss_spawn_sound.play()

        # BOSS逻辑
        if boss:
            boss.move()
            if boss.update_explosion(player, walls):
                boss_explosions.append(boss.create_explosion()); boss_roar_sound.play()
            for ex in boss_explosions[:]:
                ex["radius"] += 5
                if not ex["damaged_player"]:
                    if math.hypot(player.x - ex["x"], player.y - ex["y"]) < ex["radius"] + player.radius:
                        player.take_damage(ex["damage"]); ex["damaged_player"] = True
                        spawn_floating_text(particles, player.x, player.y - player.radius - 8, ex["damage"], FLOAT_TEXT_COLOR_PLAYER)
                        if player.health <= 0:
                            game_over = True; player_died_from_explosion = True; create_explosion(particles, player.x, player.y)
                if ex["radius"] >= ex["max_radius"]:
                    boss_explosions.remove(ex)
            if boss.collide_with_player(player) and boss.collision_cooldown <= 0:
                boss.collision_damage(player)
                spawn_floating_text(particles, player.x, player.y - player.radius - 8, (20 if boss.is_charging else 10), FLOAT_TEXT_COLOR_PLAYER)
                if player.health <= 0:
                    game_over = True; player_died_from_collision = True; create_explosion(particles, player.x, player.y)
            else:
                if boss.collision_cooldown > 0: boss.collision_cooldown -= 1

        # 玩家移动与技能
        player.move(keys, walls)
        player.update_skills()

        # Roguelike 刷怪
        rl.update_spawning(enemies, walls)

        # 道具生成
        powerup_timer += 1
        if powerup_timer >= 600 and len(powerups) < 3:
            powerups.add(PowerUp(random.randint(50, WIDTH-50), random.randint(100, HEIGHT-100)))
            powerup_timer = 0

        # 敌人移动/射击
        player_died_from_collision = False
        for enemy in list(enemies):
            col, player_died, enemy_died = enemy.move(walls, player)
            enemy.shoot_cooldown -= 1
            enemy.shoot(enemy_bullets)
            if enemy_died:
                create_explosion(particles, enemy.x, enemy.y)
                # 亡语
                try:
                    enemy.on_death(player, particles, enemies)
                except:
                    pass
                enemies.remove(enemy)
                player.score += 10
                player.add_gold(5)
                spawn_floating_text(particles, enemy.x, enemy.y, "+5g", (255, 215, 0))
                enemy_kills += 1
                # 成就触发：击杀敌人
                achievement_system.update_progress("kill_count", 1)
                if random.random() < 0.2:
                    powerups.add(PowerUp(enemy.x, enemy.y))
                continue
            if player_died:
                player_died_from_collision = True
            elif col:
                create_explosion(particles, enemy.x, enemy.y)
                spawn_floating_text(particles, player.x, player.y - player.radius - 8, 5, FLOAT_TEXT_COLOR_PLAYER)
                shake_time = 5
                shake_intensity = 3
        if player_died_from_collision:
            game_over = True
            create_explosion(particles, player.x, player.y)

        # 道具更新
        for p in list(powerups):
            if not p.update():
                powerups.remove(p)
            elif p.collide_with_player(player):
                if p.type == "health": player.health = min(100, player.health + 20)
                elif p.type == "shield": player.add_shield(20)
                else: player.score += 50
                powerup_sound.play(); powerups.remove(p)

        # 手雷
        for g in list(grenades):
            if g.update():
                create_explosion(particles, g.x, g.y, 1.5)
                all_entities = list(enemies) + [player] + ([boss] if boss else [])
                hit = g.check_explosion_collision(all_entities)
                for e in hit:
                    if e in enemies:
                        gd = player.get_grenade_damage(rl)  # 使用新的手雷伤害计算
                        e.health -= gd; e.flash = 5
                        spawn_floating_text(particles, e.x, e.y - e.radius - 8, gd, FLOAT_TEXT_COLOR_ENEMY)
                        if e.health <= 0:
                            enemies.remove(e); player.score += 15; enemy_kills += 1
                            player.add_gold(5)
                            spawn_floating_text(particles, e.x, e.y, "+5g", (255, 215, 0))
                            # 亡语
                            try:
                                e.on_death(player, particles, enemies)
                            except:
                                pass
                            # 成就触发：手雷击杀敌人
                            achievement_system.update_progress("kill_count", 1)
                            achievement_system.update_progress("weapon_kill", 1, weapon=2)  # 手雷是武器索引2
                    elif e is player:
                        base_self_damage = player.get_grenade_damage(rl) // 2
                        player.take_damage(base_self_damage)
                        spawn_floating_text(particles, player.x, player.y - player.radius - 8, base_self_damage, FLOAT_TEXT_COLOR_PLAYER)
                        if player.health <= 0:
                            game_over = True; player_died_from_explosion = True; create_explosion(particles, player.x, player.y)
                    elif boss and e is boss:
                        gd = player.get_grenade_damage(rl)  # 使用新的手雷伤害计算
                        if boss.take_damage(gd, "grenade"):
                            if boss.health <= 0:
                                create_explosion(particles, boss.x, boss.y, 2.0)
                                player.score += 500; player.add_gold(30); boss = None; boss_spawned = False
                                # 成就触发：Boss击杀
                                achievement_system.update_progress("boss_kill", 1)
                            else:
                                spawn_floating_text(particles, boss.x, boss.y - boss.radius - 10, gd, FLOAT_TEXT_COLOR_BOSS)
                shake_time = 25; shake_intensity = 15
        # 从组中移除已爆炸手雷（已由 update/kill 管理，这里确保干净）
        for g in list(grenades):
            if g.exploded and g in grenades:
                grenades.remove(g)

        # 子弹（玩家）
        for b in list(bullets):
            b.move()
            if b.off_screen():
                if b in bullets: bullets.remove(b)
                continue
            blocked = False
            for w in walls:
                if b.collide_with_wall(w) and w.block_bullet(b):
                    create_explosion(particles, b.x, b.y); bullets.remove(b); blocked = True; break
            if blocked: continue
            for e in list(enemies):
                if b.collide_with_enemy(e):
                    base_dmg = getattr(player, 'bullet_damage', 10)
                    dmg = player.get_effective_damage(base_dmg, rl)
                    e.health -= dmg
                    spawn_floating_text(particles, e.x, e.y - e.radius - 8, dmg, FLOAT_TEXT_COLOR_ENEMY)
                    if e.health <= 0:
                        create_explosion(particles, e.x, e.y)
                        if b in bullets: bullets.remove(b)
                        enemies.remove(e); player.score += 10; enemy_kills += 1
                        player.add_gold(5)
                        spawn_floating_text(particles, e.x, e.y, "+5g", (255, 215, 0))
                        # 亡语
                        try:
                            e.on_death(player, particles, enemies)
                        except:
                            pass
                        # 成就触发：子弹击杀敌人，根据武器类型记录
                        achievement_system.update_progress("kill_count", 1)
                        achievement_system.update_progress("weapon_kill", 1, weapon=player.weapon)
                        if random.random() < 0.2:
                            powerups.add(PowerUp(e.x, e.y))
                    break
            if boss and b in bullets and b.collide_with_enemy(boss):
                base_dmg = getattr(player, 'bullet_damage', 10)
                dmg = player.get_effective_damage(base_dmg, rl)
                if boss.take_damage(dmg):
                    if boss.health <= 0:
                        create_explosion(particles, boss.x, boss.y, 2.0)
                        player.score += 500; player.add_gold(30); boss = None; boss_spawned = False
                        # 成就触发：Boss击杀
                        achievement_system.update_progress("boss_kill", 1)
                    else:
                        spawn_floating_text(particles, boss.x, boss.y - boss.radius - 10, dmg, FLOAT_TEXT_COLOR_BOSS)
                if b in bullets: bullets.remove(b)

        # 子弹（敌人）
        for b in list(enemy_bullets):
            b.move()
            if b.off_screen():
                if b in enemy_bullets: enemy_bullets.remove(b)
                continue
            blocked = False
            for w in walls:
                if b.collide_with_wall(w) and w.block_bullet(b):
                    create_explosion(particles, b.x, b.y); enemy_bullets.remove(b); blocked = True; break
            if blocked: continue
            if b.collide_with_player(player):
                player.take_damage(10); create_explosion(particles, player.x, player.y)
                spawn_floating_text(particles, player.x, player.y - player.radius - 8, 10, FLOAT_TEXT_COLOR_PLAYER)
                if b in enemy_bullets: enemy_bullets.remove(b)
                if player.health <= 0: game_over = True

        # 粒子
        particles.update()

        # 房间通关：弹出奖励菜单
        if rl.room_cleared(enemies, boss) and not reward_menu.visible:
            reward_menu.visible = True
            reward_menu.build_options(player)

        # 震动
        if shake_time > 0:
            shake_offset = (random.randint(-shake_intensity, shake_intensity), random.randint(-shake_intensity, shake_intensity))
            shake_time -= 1
        else:
            shake_offset = (0, 0); shake_intensity = 0

        # 绘制
        draw_background()
        for w in walls: w.draw()
        for e in enemies: e.draw(player)
        for b in bullets: b.draw()
        for b in enemy_bullets: b.draw()
        for g in grenades: g.draw()
        player.draw()
        for p in particles: p.draw()
        for pu in powerups: pu.draw()
        if boss: boss.draw()
        for ex in boss_explosions:
            pygame.draw.circle(screen, BOSS_EXPLOSION_COLOR, (ex["x"], ex["y"]), ex["radius"])
            pygame.draw.circle(screen, (255, 100, 255, 150), (ex["x"], ex["y"]), ex["radius"], 5)
        score_text = font.render(f"Score: {player.score}", True, TEXT_COLOR)
        gold_text = font.render(f"Gold: {player.gold}", True, (255, 215, 0))
        fr_text = font.render(f"Floor {rl.floor} - Room {rl.room}  (Risk {rl.risk}/20)", True, TEXT_COLOR)
        screen.blit(score_text, (20, 25))
        screen.blit(gold_text, (20, 55))
        screen.blit(fr_text, (WIDTH - fr_text.get_width() - 20, 20))

        # 成就通知显示
        if achievement_system.has_notifications():
            ach_id = achievement_system.pop_notification()
            if ach_id and ach_id in ACHIEVEMENTS:
                ach_info = ACHIEVEMENTS[ach_id]
                # 简单的通知文本（可以做成更华丽的弹窗）
                notif_font = pygame.font.SysFont(None, 28)
                notif_text = notif_font.render(f"🎉 Achievement Unlocked: {ach_info['name']}", True, (255, 215, 0))
                notif_bg = pygame.Surface((notif_text.get_width() + 20, notif_text.get_height() + 10), pygame.SRCALPHA)
                pygame.draw.rect(notif_bg, (40, 40, 80, 200), notif_bg.get_rect(), border_radius=8)
                pygame.draw.rect(notif_bg, (255, 215, 0, 150), notif_bg.get_rect(), 2, border_radius=8)
                screen.blit(notif_bg, (WIDTH//2 - notif_bg.get_width()//2, 100))
                screen.blit(notif_text, (WIDTH//2 - notif_text.get_width()//2, 105))
        enemies_text = small_font.render(f"Enemies: {len(enemies)}/{rl.cap}", True, (200, 150, 150))
        screen.blit(enemies_text, (WIDTH - enemies_text.get_width() - 20, 60))
        draw_health_bar(player, 150, 25, 200, 20)
        draw_weapon_indicator(20, HEIGHT - 120, player.weapon)
        draw_ui_panel(player)
        if boss_warning_timer[0] > 0:
            warning_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alpha = int(abs(math.sin(pygame.time.get_ticks() / 200)) * 200)
            warning_surface.fill((255, 50, 50, alpha))
            screen.blit(warning_surface, (0, 0))
            warning_font = pygame.font.SysFont(None, 72)
            wt = warning_font.render("BOSS INCOMING!", True, (255, 255, 255))
            screen.blit(wt, (WIDTH//2 - wt.get_width()//2, HEIGHT//2 - 50))
        if shake_offset != (0, 0):
            tmp = pygame.Surface((WIDTH, HEIGHT))
            tmp.blit(screen, (0, 0))
            screen.blit(tmp, shake_offset)
        if pause_menu.visible:
            pause_menu.draw()
        pygame.display.flip(); clock.tick(60)

if __name__ == "__main__":
    main()


