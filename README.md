# ZKWhiteCastle

A small Pygame-powered roguelite card-battle prototype inspired by Kingdom Hearts: Chain of Memories. 

## Installation

1. Clone or download this repo to your machine.  
2. Ensure you have Python 3.7+ installed.  
3. Install dependencies:  
   ```bash
   pip install pygame
   ```
4. Place `ZKWhiteCastle.py` in your working folder.

## Running the Game

```bash
python ZKWhiteCastle.py
```

A window will open at 800×600. Close it or press the window’s close button to quit.

## Controls

| Action             | Key           |
|--------------------|---------------|
| Move player        | W / A / S / D |
| Cycle cards        | ← / →         |
| Play selected card | SPACEBAR      |

## Gameplay Mechanics

1. **Starting Deck**  
   – 10 cards total:  
     – 3× Attack  
     – 3× Heal  
     – 2× Defense  
     – 2× Buff  

2. **Hand & Carousel**  
   – Always hold 3 cards in hand.  
   – Cycle left/right to bring one into the center.  
   – Cards scale and slide to simulate a ring.

3. **Playing a Card**  
   – Press SPACE to use the center card.  
   – Triggers the card’s effect (damage, heal, buff, etc.).  
   – Discards the used card, immediately draws a replacement (if available), and auto-rotates the carousel.


4. **Deck & Discard Counters**  
   – On-screen display shows remaining draw-pile and discard-pile counts.

## Code Structure

`ZKWhiteCastle.py` (single-file prototype)  
- `class Card`  
- `class Deck` (no automatic reshuffle; deck truly drains)  
- `class Player` (movement, hand & carousel, `use_card()`, Limit Break)  
- `class Enemy` (simple AI, its own deck & hand)  
- `main()` loop: input, update, draw, stage progression

## Future Improvements

- Post-battle rewards & deck expansion  
- Consumable/exhaust cards (one-time use)  
- Enemy deck variety & smarter AI  
- Map/floor system for roguelite progression  
- Card art & animations  
- Save/load runs and high-score tracking

## Acknowledgments

Inspired by the card-based combat of Kingdom Hearts: Chain of Memories and modern roguelite deckbuilders.
