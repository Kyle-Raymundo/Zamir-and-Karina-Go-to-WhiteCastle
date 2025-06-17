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
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Clock for controlling the frame rate
clock = pygame.time.Clock()
FPS = 60

# Player class
class Player:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = 5
        self.max_health = 100
        self.health = 100
        self.attack_power = 10
        self.defense = 0
        self.deck = Deck()
        self.turn = True

    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))

    def draw_cards(self, screen):
        for i, card in enumerate(self.deck.hand):
            pygame.draw.rect(screen, BLUE, (50 + i * 100, SCREEN_HEIGHT - 100, 80, 120))
            font = pygame.font.SysFont("Arial", 20)
            text = font.render(card.name, True, WHITE)
            screen.blit(text, (50 + i * 100 + 10, SCREEN_HEIGHT - 90))

    def use_card(self, card, enemy):
        card.effect(self, enemy)

# Enemy class
class Enemy:
    def __init__(self, stage):
        self.health = 80 + stage * 20
        self.attack_power = 10 + stage * 5
        self.defense = 0
        self.deck = Deck()

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH - 100, 100, 50, 50))

    def take_turn(self, player):
        card = random.choice(self.deck.hand)
        print(f"Enemy uses {card.name} card!")
        card.effect(self, player)

# Card Class
class Card:
    def __init__(self, name, effect):
        self.name = name
        self.effect = effect

# Deck Class
class Deck:
    def __init__(self):
        self.hand = self.create_deck()

    def create_deck(self):
        attack_card = Card("Attack", self.attack_effect)
        heal_card = Card("Heal", self.heal_effect)
        defense_card = Card("Defense", self.defense_effect)
        buff_card = Card("Buff", self.buff_effect)
        return [attack_card, heal_card, defense_card, buff_card]

    def draw_card(self):
        return random.choice(self.hand)

    def attack_effect(self, player, enemy):
        damage = max(0, player.attack_power - enemy.defense)
        enemy.health -= damage
        print(f"Attack! Enemy's health is now: {enemy.health}")

    def heal_effect(self, player, enemy):
        player.health += 10
        print(f"Heal! Player's health is now: {player.health}")

    def defense_effect(self, player, enemy):
        player.defense += 5
        print(f"Defense! Player's defense is now: {player.defense}")

    def buff_effect(self, player, enemy):
        player.attack_power += 5
        print(f"Buff! Player's attack power is now: {player.attack_power}")

def main():
    running = True
    player = Player(400, 300, 50, 50)
    stage = 1
    max_stages = 3
    enemy = Enemy(stage)
    selected_card = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and player.turn:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for i, card in enumerate(player.deck.hand):
                    if 50 + i * 100 < mouse_x < 50 + (i + 1) * 100 and SCREEN_HEIGHT - 100 < mouse_y < SCREEN_HEIGHT - 100 + 120:
                        selected_card = card
                        print(f"Selected {card.name} card!")

        if selected_card and player.turn:
            player.use_card(selected_card, enemy)
            selected_card = None
            player.turn = False
            pygame.time.delay(300)
            enemy.take_turn(player)
            player.turn = True

        if enemy.health <= 0:
            stage += 1
            if stage > max_stages:
                print("You Win!")
                pygame.time.delay(2000)
                running = False
            else:
                enemy = Enemy(stage)
                player.health = min(player.health + 20, player.max_health)
                player.attack_power += 2
                player.defense += 1
                print("Next enemy!")

        if player.health <= 0:
            print("Game Over!")
            pygame.time.delay(2000)
            running = False

        keys = pygame.key.get_pressed()
        player.move(keys)

        screen.fill(WHITE)
        player.draw(screen)
        player.draw_cards(screen)
        enemy.draw(screen)

        font_ui = pygame.font.SysFont("Arial", 24)
        player_health_text = font_ui.render(f"Player HP: {player.health}", True, BLACK)
        enemy_health_text = font_ui.render(f"Enemy HP: {enemy.health}", True, BLACK)
        screen.blit(player_health_text, (20, 20))
        screen.blit(enemy_health_text, (SCREEN_WIDTH - 200, 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
