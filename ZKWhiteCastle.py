import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ZKWhiteCastle")

# Colors
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (255, 0,   0)
BLUE   = (0,   0, 255)
GREEN  = (0, 255,   0)
YELLOW = (255, 255,  0)

# Clock
clock = pygame.time.Clock()
FPS   = 60

class Card:
    def __init__(self, name, effect):
        self.name   = name
        self.effect = effect

class Deck:
    def __init__(self):
        self.draw_pile    = self.create_deck()
        random.shuffle(self.draw_pile)
        self.discard_pile = []

    def create_deck(self):
        # Exactly 10 starting cards:
        # 3× Attack, 3× Heal, 2× Defense, 2× Buff
        deck = []
        for _ in range(3):
            deck.append(Card("Attack",  Deck.attack_effect))
        for _ in range(3):
            deck.append(Card("Heal",    Deck.heal_effect))
        for _ in range(2):
            deck.append(Card("Defense", Deck.defense_effect))
        for _ in range(2):
            deck.append(Card("Buff",    Deck.buff_effect))
        return deck

    def draw_card(self):
        # No reshuffle: if empty, return None
        return self.draw_pile.pop() if self.draw_pile else None

    def has_cards(self):
        # Only true while draw_pile has cards
        return bool(self.draw_pile)

    def discard_card(self, card):
        self.discard_pile.append(card)

    # Static effect methods
    @staticmethod
    def attack_effect(player, enemy):
        dmg = max(0, player.attack_power - enemy.defense)
        enemy.health -= dmg
        print(f"Attack! Enemy HP: {enemy.health}")

    @staticmethod
    def heal_effect(player, enemy):
        player.health += 10
        print(f"Heal! Player HP: {player.health}")

    @staticmethod
    def defense_effect(player, enemy):
        player.defense += 5
        print(f"Defense! Player DEF: {player.defense}")

    @staticmethod
    def buff_effect(player, enemy):
        player.attack_power += 5
        print(f"Buff! Player ATK: {player.attack_power}")

class Player:
    def __init__(self, x, y, w, h):
        self.x              = x
        self.y              = y
        self.width          = w
        self.height         = h
        self.speed          = 5
        self.max_health     = 100
        self.health         = 100
        self.attack_power   = 10
        self.defense        = 0
        self.deck           = Deck()
        self.hand           = []
        self.hand_size      = 3
        self.turn           = True
        self.selected_index = 0

        # Carousel animation
        self.carousel_offset = 0
        self.target_offset   = 0
        self.rotation_queue  = 0
        self.anim_speed      = 0.05

        # Limit Break
        self.limit_break       = False
        self.limit_break_turns = 0

        self.draw_starting_hand()

    def draw_starting_hand(self):
        for _ in range(self.hand_size):
            self.draw_card()

    def draw_card(self):
        c = self.deck.draw_card()
        if c:
            self.hand.append(c)

    def move(self, keys):
        if keys[pygame.K_a]: self.x -= self.speed
        if keys[pygame.K_d]: self.x += self.speed
        if keys[pygame.K_w]: self.y -= self.speed
        if keys[pygame.K_s]: self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))

    def draw_cards(self, screen):
        center_x = 200
        center_y = 60
        card_w   = 50
        card_h   = 70
        spacing  = 35

        n = len(self.hand)
        if n == 0:
            return

        for offset in (-1, 0, 1):
            if n < 2 and abs(offset) > n - 1:
                continue

            pos_off = offset + self.carousel_offset
            idx     = (self.selected_index + offset) % n
            card    = self.hand[idx]

            px   = center_x + pos_off * spacing
            dist = abs(pos_off)
            scale = max(0.8, 1 - 0.2 * dist)
            dw = int(card_w * scale)
            dh = int(card_h * scale)
            rect = pygame.Rect(px - dw//2,
                               center_y + (card_h - dh),
                               dw, dh)

            color = YELLOW if offset==0 and self.carousel_offset==0 else BLUE
            pygame.draw.rect(screen, color, rect)
            f   = pygame.font.SysFont("Arial", 16)
            txt = f.render(card.name, True, WHITE)
            screen.blit(txt, (rect.x+5, rect.y+5))

    def cycle_left(self):
        if self.rotation_queue==0 and len(self.hand)>1:
            self.rotation_queue = -1
            self.target_offset += 1

    def cycle_right(self):
        if self.rotation_queue==0 and len(self.hand)>1:
            self.rotation_queue = 1
            self.target_offset -= 1

    def update_animation(self):
        if self.carousel_offset != self.target_offset:
            dir = 1 if self.carousel_offset < self.target_offset else -1
            self.carousel_offset += self.anim_speed * dir
            if abs(self.carousel_offset - self.target_offset) < self.anim_speed:
                self.carousel_offset = self.target_offset

        if self.carousel_offset == self.target_offset and self.rotation_queue!=0:
            self.selected_index = (self.selected_index - self.rotation_queue) % len(self.hand)
            self.carousel_offset = 0
            self.target_offset   = 0
            self.rotation_queue  = 0

    def use_card(self, enemy):
        # Block if no cards & no limit break
        if not self.hand and not self.limit_break:
            print("No cards left!")
            return

        # Limit Break spam
        if self.limit_break:
            enemy.health -= self.attack_power
            print(f"LIMIT BREAK ATTACK! Enemy HP: {enemy.health}")
            self.limit_break_turns -= 1
            if self.limit_break_turns <= 0:
                self.limit_break = False
                print("Limit Break ended.")
            return

        # Play + discard
        card = self.hand[self.selected_index]
        card.effect(self, enemy)
        self.deck.discard_card(card)

        # Remove and draw replacement
        self.hand.pop(self.selected_index)
        new_card = self.deck.draw_card()
        if new_card:
            self.hand.insert(self.selected_index, new_card)

        # Clamp index
        if self.selected_index >= len(self.hand):
            self.selected_index = max(0, len(self.hand)-1)

        # Spin carousel
        if len(self.hand) > 1:
            self.cycle_left()

        # Trigger Limit Break when truly empty
        if not self.hand and not self.deck.draw_pile and not self.deck.discard_pile:
            self.limit_break = True
            self.limit_break_turns = 5
            print("LIMIT BREAK ACTIVATED!")

class Enemy:
    def __init__(self, stage):
        self.health       = 80 + stage*20
        self.attack_power = 10 + stage*5
        self.defense      = 0
        self.deck         = Deck()
        self.hand         = []
        self.hand_size    = 4
        self.draw_starting_hand()

    def draw_starting_hand(self):
        for _ in range(self.hand_size):
            c = self.deck.draw_card()
            if c: self.hand.append(c)

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN,
                         (SCREEN_WIDTH-100, 100, 50, 50))

    def take_turn(self, player):
        if not self.hand:
            c = self.deck.draw_card()
            if c: self.hand.append(c)
        if self.hand:
            card = random.choice(self.hand)
            print(f"Enemy uses {card.name}")
            card.effect(self, player)
            self.hand.remove(card)
            self.deck.discard_card(card)
            # draw replacement
            c2 = self.deck.draw_card()
            if c2: self.hand.append(c2)

def main():
    player = Player(400,300,50,50)
    stage  = 1
    max_stages = 3
    enemy  = Enemy(stage)
    running = True

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if ev.type==pygame.KEYDOWN and player.turn and player.rotation_queue==0:
                if ev.key==pygame.K_LEFT:
                    player.cycle_left()
                if ev.key==pygame.K_RIGHT:
                    player.cycle_right()
                if ev.key==pygame.K_SPACE and player.carousel_offset==0:
                    player.use_card(enemy)
                    player.turn = False
                    pygame.time.delay(300)
                    enemy.take_turn(player)
                    player.turn = True

        # Stage progression
        if enemy.health <= 0:
            stage += 1
            if stage > max_stages:
                print("You Win!")
                pygame.time.delay(2000)
                running = False
            else:
                enemy = Enemy(stage)
                player.health       = min(player.health + 20,
                                          player.max_health)
                player.attack_power += 2
                player.defense      += 1
                print("Next enemy!")

        if player.health <= 0:
            print("Game Over!")
            pygame.time.delay(2000)
            running = False

        # Update & draw
        keys = pygame.key.get_pressed()
        player.move(keys)
        player.update_animation()

        screen.fill(WHITE)
        player.draw(screen)
        player.draw_cards(screen)
        enemy.draw(screen)

        # UI
        font_ui = pygame.font.SysFont("Arial", 24)
        screen.blit(font_ui.render(f"Player HP: {player.health}", True, BLACK),
                    (20, 20))
        screen.blit(font_ui.render(f"Enemy  HP: {enemy.health}",  True, BLACK),
                    (SCREEN_WIDTH-200, 20))
        screen.blit(font_ui.render(f"Deck:    {len(player.deck.draw_pile)}", True, BLACK),
                    (20, 50))
        screen.blit(font_ui.render(f"Discard: {len(player.deck.discard_pile)}", True, BLACK),
                    (20, 80))
        if player.limit_break:
            screen.blit(font_ui.render(f"LIMIT BREAK! ({player.limit_break_turns})",
                                       True, RED),
                        (SCREEN_WIDTH//2-100, 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
