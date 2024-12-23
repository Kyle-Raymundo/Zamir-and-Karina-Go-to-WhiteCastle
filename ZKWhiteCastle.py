import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("_ZKWhiteCastle")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # Color for the player
BLUE = (0, 0, 255)  # Color for the card
GREEN = (0, 255, 0)  # Color for the enemy

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
        self.health = 100
        self.attack_power = 10
        self.defense = 0
        self.deck = Deck()  # Player's deck
        self.turn = True  # To check if it's the player's turn

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
        # Draw the cards in the player's hand
        for i, card in enumerate(self.deck.hand):
            pygame.draw.rect(screen, BLUE, (50 + i * 100, SCREEN_HEIGHT - 100, 80, 120))  # Card position
            font = pygame.font.SysFont("Arial", 20)
            text = font.render(card.name, True, WHITE)
            screen.blit(text, (50 + i * 100 + 10, SCREEN_HEIGHT - 90))  # Card name text

    def use_card(self, card, enemy):
        card.effect(self, enemy)

# Enemy class
class Enemy:
    def __init__(self):
        self.health = 100
        self.attack_power = 10
        self.defense = 0
        self.deck = Deck()  # Enemy's deck

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH - 100, 100, 50, 50))

    def take_turn(self, player):
        # Simple AI: The enemy randomly selects a card to play
        card = random.choice(self.deck.hand)
        print(f"Enemy uses {card.name} card!")
        card.effect(self, player)

# Card Class
class Card:
    def __init__(self, name, effect):
        self.name = name
        self.effect = effect  # The effect function the card will trigger

# Deck Class
class Deck:
    def __init__(self):
        self.hand = self.create_deck()

    def create_deck(self):
        # Create a deck with different types of cards
        attack_card = Card("Attack", self.attack_effect)
        heal_card = Card("Heal", self.heal_effect)
        defense_card = Card("Defense", self.defense_effect)
        buff_card = Card("Buff", self.buff_effect)
        return [attack_card, heal_card, defense_card, buff_card]

    def draw_card(self):
        return random.choice(self.hand)

    def attack_effect(self, player, enemy):
        # Effect of the attack card (deal damage)
        damage = max(0, player.attack_power - enemy.defense)  # Apply defense
        enemy.health -= damage
        print(f"Attack! Enemy's health is now: {enemy.health}")

    def heal_effect(self, player, enemy):
        # Effect of the heal card (restore health)
        player.health += 10
        print(f"Heal! Player's health is now: {player.health}")

    def defense_effect(self, player, enemy):
        # Effect of the defense card (increase defense)
        player.defense += 5
        print(f"Defense! Player's defense is now: {player.defense}")

    def buff_effect(self, player, enemy):
        # Effect of the buff card (increase attack power)
        player.attack_power += 5
        print(f"Buff! Player's attack power is now: {player.attack_power}")

def main():
    running = True
    player = Player(400, 300, 50, 50)  # Create a player object
    enemy = Enemy()  # Create an enemy object
    selected_card = None  # Track the selected card

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Select a card when the player clicks on it (for simplicity, just clicking on the cards)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for i, card in enumerate(player.deck.hand):
                    if 50 + i * 100 < mouse_x < 50 + (i + 1) * 100 and SCREEN_HEIGHT - 100 < mouse_y < SCREEN_HEIGHT - 100 + 120:
                        selected_card = card
                        print(f"Selected {card.name} card!")

        # Use the selected card
        if selected_card and player.turn:
            player.use_card(selected_card, enemy)
            selected_card = None  # Reset the selection after using the card
            player.turn = False  # End player's turn
            enemy.take_turn(player)  # Enemy takes its turn
            player.turn = True  # Back to player's turn

        # Game logic updates
        keys = pygame.key.get_pressed()
        player.move(keys)

        # Rendering
        screen.fill(WHITE)  # Clear the screen with white
        player.draw(screen)  # Draw the player
        player.draw_cards(screen)  # Draw the player's cards
        enemy.draw(screen)  # Draw the enemy

        pygame.display.flip()  # Update the display

        # Control frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
0