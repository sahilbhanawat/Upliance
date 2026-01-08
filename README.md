# Rock-Paper-Scissors-Plus: AI Game Referee

A CLI-based Rock-Paper-Scissors-Plus game with an automated bot opponent.

## Quick Start

```bash
python referee.py
```

No API key or external dependencies required!

## Game Rules

1. **Best of 3 Rounds**: First to 2 wins, or highest score after 3 rounds.
2. **Valid Moves**: `rock`, `paper`, `scissors`, `bomb`
3. **Bomb**: Beats everything except another bomb (draw). **One-time use per player.**
4. **Invalid Input**: Wastes the round (no points, round still counts).
5. **Auto-End**: Game ends after at most 3 rounds.

---

## Architecture & Design

### State Model (`GameState` class)

| Field             | Type   | Description                     |
|-------------------|--------|---------------------------------|
| `round_number`    | int    | Current round (0-3)             |
| `user_score`      | int    | User's total wins               |
| `bot_score`       | int    | Bot's total wins                |
| `user_bomb_used`  | bool   | Has user spent their bomb?       |
| `bot_bomb_used`   | bool   | Has bot spent their bomb?        |
| `game_over`       | bool   | Is the game finished?           |
| `result_message`  | str    | Final result announcement       |

### Separation of Concerns (ADK-Style)

1. **Intent Understanding** (`main()`): Parses user input, handles quit commands
2. **Game Logic** (`submit_move` tool): Validates moves, resolves rounds, updates state
3. **Response Generation** (`format_round_result()`): Creates human-readable output

### Tool Design (`submit_move`)

```python
def submit_move(game_state: GameState, user_move: str) -> dict:
    """
    - Validates the move (including bomb restrictions).
    - Generates the bot's move (random, 20% bomb chance if available).
    - Resolves the round.
    - Updates game state.
    - Returns structured result dict.
    """
```

---

## Tradeoffs

| Decision                        | Rationale                                           |
|---------------------------------|-----------------------------------------------------|
| Single tool (`submit_move`)     | Simplicity; game is small. Clean atomic operations. |
| Random bot moves                | Simple, unpredictable. Could add strategy later.    |
| "Invalid = wasted round"        | Per spec. Alternative: prompt again.                |
| No external dependencies        | Runs anywhere with just Python 3.                   |

---

## What I Would Improve

1. **LLM Integration**: Add optional Gemini referee for natural language commentary
2. **Smarter Bot**: Pattern recognition or counter-strategy
3. **Unit Tests**: Pytest suite for `GameState` edge cases
4. **Replay System**: Save and replay games

---

## Example Session

```
==================================================
   🎯 ROCK-PAPER-SCISSORS-PLUS 🎯
==================================================

📋 RULES:
1. Best of 3 rounds (first to 2 wins)
2. Moves: rock, paper, scissors, bomb
3. Bomb beats all (once per player). Bomb vs bomb = draw.
4. Invalid input wastes the round.
5. Game ends after max 3 rounds.

🎮 Score - You: 0, Bot: 0 | Bomb left - You: Yes, Bot: Yes
--------------------------------------------------
Round 1 - Your move: rock

🎮 Round 1
   You: ROCK  vs  Bot: SCISSORS
   ➡️  You WIN this round!
   📊 Score: You 1 - 0 Bot

🎮 Score - You: 1, Bot: 0 | Bomb left - You: Yes, Bot: Yes
--------------------------------------------------
Round 2 - Your move: bomb

🎮 Round 2
   You: BOMB  vs  Bot: PAPER
   ➡️  You WIN this round!
   📊 Score: You 2 - 0 Bot

==================================================
   🎉 YOU WIN THE GAME!
==================================================

🎮 Thanks for playing!
```
