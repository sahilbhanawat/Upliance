# Rock-Paper-Scissors-Plus: Game Referee

A CLI-based Rock-Paper-Scissors-Plus game with an automated bot opponent.

---

## Quick Start

```bash
python referee.py
```

No dependencies required. Works with Python 3.6+.

---

## Game Rules

| Rule | Description |
|------|-------------|
| Best of 3 | First to 2 wins, or highest score after 3 rounds |
| Valid Moves | `rock`, `paper`, `scissors`, `bomb` |
| Bomb | Beats everything except another bomb (draw). One use per player. |
| Invalid Input | Wastes the round - no points, round counts |
| Auto-End | Game ends after at most 3 rounds |

---

## Architecture

### State Model

The `GameState` class tracks all game state:

```
round_number    : int   - Current round (0-3)
user_score      : int   - User's wins
bot_score       : int   - Bot's wins  
user_bomb_used  : bool  - Has user used bomb?
bot_bomb_used   : bool  - Has bot used bomb?
game_over       : bool  - Is game finished?
result_message  : str   - Final result text
```

### Separation of Concerns

The code follows ADK-style separation:

| Layer | Function | Responsibility |
|-------|----------|----------------|
| Intent Understanding | `main()` | Parse user input, handle quit commands |
| Game Logic | `submit_move()` | Validate moves, resolve rounds, update state |
| Response Generation | `format_round_result()` | Create human-readable output |

### Tool Design

The `submit_move(game_state, user_move)` function is the core ADK tool:

- Validates the move (including bomb restrictions)
- Generates bot's move (random, 20% bomb chance if available)
- Resolves the round winner
- Updates game state
- Returns structured result dictionary

---

## Tradeoffs

| Decision | Rationale |
|----------|-----------|
| Single tool | Simplicity; game is small enough for atomic operations |
| Random bot moves | Simple and unpredictable; could add strategy later |
| Invalid = wasted round | Per specification; alternative would be re-prompting |
| No external deps | Runs anywhere with just Python |

---

## Improvements for Future

- LLM integration for natural language commentary
- Smarter bot with pattern recognition
- Unit test suite for edge cases
- Game replay and save functionality

---

## Example Session

```
==================================================
   ROCK-PAPER-SCISSORS-PLUS
==================================================

RULES:
1. Best of 3 rounds (first to 2 wins)
2. Moves: rock, paper, scissors, bomb
3. Bomb beats all (once per player). Bomb vs bomb = draw.
4. Invalid input wastes the round.
5. Game ends after max 3 rounds.

Score - You: 0, Bot: 0 | Bomb left - You: Yes, Bot: Yes
--------------------------------------------------
Round 1 - Your move: rock

Round 1
   You: ROCK  vs  Bot: SCISSORS
   --> You WIN this round!
   Score: You 1 - 0 Bot

Score - You: 1, Bot: 0 | Bomb left - You: Yes, Bot: Yes
--------------------------------------------------
Round 2 - Your move: bomb

Round 2
   You: BOMB  vs  Bot: PAPER
   --> You WIN this round!
   Score: You 2 - 0 Bot

==================================================
   YOU WIN THE GAME!
==================================================

Thanks for playing!
```
