import pygame
import sys
import random
import math

# ─────────────────────────────────────────
#  Initialisation s
# ─────────────────────────────────────────
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ZKWhiteCastle – Arena Build")

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (255, 0,   0)
BLUE   = (0,   0, 255)
GREEN  = (0, 255,   0)
YELLOW = (255, 255,  0)

clock = pygame.time.Clock()
FPS = 60

GRAVITY       = 0.6
JUMP_VELOCITY = -12
MOVE_SPEED    = 5

platforms = [pygame.Rect(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)]

class Card:
    def __init__(self, name, effect):
        self.name = name
        self.effect = effect

class Deck:
    def __init__(self):
        self.draw_pile = self._create_deck()
        random.shuffle(self.draw_pile)
        self.discard_pile = []

    def _create_deck(self):
        return ([Card("Attack", Deck.attack_effect)] * 3 +
                [Card("Heal",   Deck.heal_effect)]   * 3 +
                [Card("Defense",Deck.defense_effect)]* 2 +
                [Card("Buff",   Deck.buff_effect)]   * 2)

    def draw_card(self):
        return self.draw_pile.pop() if self.draw_pile else None

    def discard_card(self, card):
        self.discard_pile.append(card)

    @staticmethod
    def attack_effect(player, enemy):
        if player.can_hit(enemy):
            enemy.health -= player.attack_power
            print(f"Attack hits!  Enemy HP: {enemy.health}")
        else:
            print("Attack missed – out of range / not facing.")

    @staticmethod
    def heal_effect(player, _):
        player.health = min(player.max_health, player.health + 10)
        print(f"Heal +10 ▶ Player HP: {player.health}")

    @staticmethod
    def defense_effect(player, _):
        player.defense += 5
        print(f"Defense +5 ▶ DEF: {player.defense}")

    @staticmethod
    def buff_effect(player, _):
        player.attack_power += 5
        print(f"Buff +5 ▶ ATK: {player.attack_power}")

class Entity:
    def __init__(self, x, y, w, h, color):
        self.x, self.y = x, y
        self.width, self.height = w, h
        self.color = color
        self.vx, self.vy = 0, 0
        self.on_ground = False

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def apply_gravity(self):
        self.vy += GRAVITY
        self.y += self.vy

        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat) and self.vy >= 0:
                self.y = plat.top - self.height
                self.vy = 0
                self.on_ground = True

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40, RED)
        self.max_health = 100
        self.health = 100
        self.attack_power = 10
        self.defense = 0
        self.facing = 'right'
        self.deck = Deck()
        self.hand = []
        self.hand_size = 3
        self.draw_starting_hand()
        self.selected_index = 0
        self.carousel_offset = 0
        self.target_offset = 0
        self.rotation_queue = 0
        self.anim_speed = 0.1
        self.limit_break = False
        self.limit_break_turns = 0

    def draw_starting_hand(self):
        for _ in range(self.hand_size):
            self.draw_card()

    def draw_card(self):
        c = self.deck.draw_card()
        if c:
            self.hand.append(c)

    def handle_input(self, keys):
        self.vx = 0
        if keys[pygame.K_a]:
            self.vx = -MOVE_SPEED
            self.facing = 'left'
        elif keys[pygame.K_d]:
            self.vx = MOVE_SPEED
            self.facing = 'right'
        if keys[pygame.K_w] and self.on_ground:
            self.vy = JUMP_VELOCITY
            self.on_ground = False

    def update(self):
        self.x += self.vx
        self.apply_gravity()
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))

    def can_hit(self, enemy, reach=60, vertical_tolerance=40):
        dx = (enemy.x + enemy.width/2) - (self.x + self.width/2)
        dy = abs((enemy.y + enemy.height/2) - (self.y + self.height/2))
        if dy > vertical_tolerance:
            return False
        if self.facing == 'right' and dx < 0:
            return False
        if self.facing == 'left' and dx > 0:
            return False
        return abs(dx) <= reach

    def cycle_left(self):
        if self.rotation_queue==0 and len(self.hand)>1:
            self.rotation_queue=-1; self.target_offset=1

    def cycle_right(self):
        if self.rotation_queue==0 and len(self.hand)>1:
            self.rotation_queue=1; self.target_offset=-1

    def update_carousel(self):
        if self.rotation_queue!=0:
            step=self.anim_speed*(1 if self.target_offset>self.carousel_offset else -1)
            self.carousel_offset+=step
            if abs(self.carousel_offset-self.target_offset)<self.anim_speed:
                self.carousel_offset=self.target_offset
                if len(self.hand) > 0:
                    self.selected_index=(self.selected_index-self.rotation_queue)%len(self.hand)
                self.carousel_offset=self.target_offset=0; self.rotation_queue=0

    def use_card(self, enemy):
        if not self.hand and not self.limit_break:
            return

        if self.limit_break:
            if self.can_hit(enemy):
                enemy.health -= self.attack_power
                print(f"LIMIT BREAK HIT!  Enemy HP: {enemy.health}")
            else:
                print("Limit Break missed.")
            self.limit_break_turns -= 1
            if self.limit_break_turns <= 0:
                self.limit_break = False
                print("Limit Break ended.")
            return

        card = self.hand[self.selected_index]
        card.effect(self, enemy)
        self.deck.discard_card(card)
        self.hand.pop(self.selected_index)

        rep = self.deck.draw_card()
        if rep:
            self.hand.insert(self.selected_index, rep)
        if self.selected_index >= len(self.hand):
            self.selected_index = max(0, len(self.hand) - 1)

        if not self.hand and not self.deck.draw_pile:
            self.limit_break = True
            self.limit_break_turns = 5
            print("LIMIT BREAK ACTIVATED!")

    def draw_hand(self, surf):
        center_x, center_y = 200, 60
        card_w, card_h = 50, 70
        spacing = 40
        n = len(self.hand)
        if n == 0:
            return
        for offset in (-1, 0, 1):
            if n < 2 and offset:
                continue
            pos = offset + self.carousel_offset
            idx = (self.selected_index + offset) % n if n > 0 else 0
            card = self.hand[idx]
            px = center_x + pos * spacing
            scale = max(0.75, 1 - 0.3 * abs(pos))
            dw, dh = int(card_w * scale), int(card_h * scale)
            rect = pygame.Rect(px - dw // 2, center_y + (card_h - dh), dw, dh)
            col = YELLOW if offset == 0 and abs(self.carousel_offset) < 0.05 else BLUE
            pygame.draw.rect(surf, col, rect)
            txt = pygame.font.SysFont("Arial", 14).render(card.name, True, WHITE)
            surf.blit(txt, (rect.x + 4, rect.y + 4))

class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40, GREEN)
        self.health = 150

player = Player(100, SCREEN_HEIGHT - 80)
enemy = Enemy(600, SCREEN_HEIGHT - 80)
running = True

while running:
    dt = clock.tick(FPS) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.cycle_right()
            if event.key == pygame.K_RIGHT:
                player.cycle_left()
            if event.key == pygame.K_SPACE:
                player.use_card(enemy)

    keys = pygame.key.get_pressed()
    player.handle_input(keys)

    player.update()
    player.update_carousel()

    screen.fill(WHITE)
    for plat in platforms: pygame.draw.rect(screen, BLACK, plat)
    player.draw(screen)
    enemy.draw(screen)
    player.draw_hand(screen)

    ui = pygame.font.SysFont("Arial", 20)
    screen.blit(ui.render(f"Player HP {player.health}", True, BLACK), (20, 20))
    screen.blit(ui.render(f"Enemy HP {enemy.health}", True, BLACK), (SCREEN_WIDTH - 180, 20))
    if player.limit_break:
        screen.blit(ui.render(f"LIMIT BREAK ({player.limit_break_turns})", True, RED), (SCREEN_WIDTH//2 - 80, 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
