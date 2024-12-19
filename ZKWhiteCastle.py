import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ZKWhiteCastle")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0) #Current color for player
BLUE = (0, 0, 255)  # Color for the card
GREEN = (0, 255, 0) #color for the enemy

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
        self.speed = 5  # Movement speed
        self.health = 100
        self.deck = Deck() #player deck

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
        #Draw the cards in the player's hand.
        for i, card in enumerate(self.deck.hand):
            pygame.draw.rect(screen, BLUE, (50 + i * 100, SCREEN_HEIGHT - 100, 80, 120))  # Card position
            font = pygame.font.SysFont("comicsansms", 20)
            text = font.render(card.name, True, WHITE)
            screen.blit(text, (50 + i * 100 + 10, SCREEN_HEIGHT - 90))  # Card name text
    def use_card(self, card):
        card.effect(self)
#Card Class
class Card:
    def __init__(self, name, effect):
        self.name = name
        self.effect = effect  # The effect function the card will trigger
class Deck:
    def __init__(self):
        self.hand = self.create_deck()

    def create_deck(self):
        # Create a deck with different types of cards
        attack_card = Card("Attack", self.attack_effect)
        heal_card = Card("Heal", self.heal_effect)
        return [attack_card, heal_card]

    def draw_card(self):
        return random.choice(self.hand)

    def attack_effect(self, player):
        # Effect of the attack card (deal damage)
        player.health -= 10
        print("Attack! Player's health is now:", player.health)

    def heal_effect(self, player):
        # Effect of the heal card (restore health)
        player.health += 10
        print("Heal! Player's health is now:", player.health)
def main():
    running = True
    player = Player(400, 300, 50, 50)  # Create a player object
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
        if selected_card:
            player.use_card(selected_card)
            selected_card = None  # Reset the selection after using the card

        # Game logic updates
        keys = pygame.key.get_pressed()
        player.move(keys)

        # Rendering
        screen.fill(WHITE)  # Clear the screen with white
        player.draw(screen)  # Draw the player
        player.draw_cards(screen)  # Draw the player's cards

        pygame.display.flip()  # Update the display

        # Control frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()