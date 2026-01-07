# Rock-Paper-Scissors-Plus: AI Game Referee

A CLI-based Rock-Paper-Scissors-Plus game where an AI (powered by Google Gemini) acts as a fair referee, enforcing rules and tracking game state.

## Quick Start

```bash
# 1. Install dependencies
pip install google-genai

# 2. Set your API key
# Windows PowerShell:
$env:GOOGLE_API_KEY = "your-api-key-here"
# Or Linux/Mac:
# export GOOGLE_API_KEY="your-api-key-here"

# 3. Run the game
python referee.py
```

## Game Rules

1. **Best of 3 Rounds**: First to 2 wins, or highest score after 3 rounds.
2. **Valid Moves**: `rock`, `paper`, `scissors`, `bomb`
3. **Bomb**: Beats everything except another bomb (draw). **One-time use per player.**
4. **Invalid Input**: Wastes the round (no points, round still counts).
5. **Auto-End**: Game ends after at most 3 rounds.

---

## Architecture & Design

### State Model (`GameState` class)

| Field             | Type   | Description                                    |
|-------------------|--------|------------------------------------------------|
| `round_number`    | int    | Current round (0-3)                            |
| `user_score`      | int    | User's total wins                              |
| `bot_score`       | int    | Bot's total wins                               |
| `user_bomb_used`  | bool   | Has user spent their bomb?                     |
| `bot_bomb_used`   | bool   | Has bot spent their bomb?                      |
| `game_over`       | bool   | Is the game finished?                          |
| `result_message`  | str    | Final result announcement                      |

**Key Methods:**
- `is_valid_move(move)`: Checks if input is rock/paper/scissors/bomb.
- `can_use_bomb(player)`: Returns True if bomb is still available.
- `resolve(user_move, bot_move)`: Determines round winner.
- `check_game_over()`: Evaluates win conditions.

### Tool Design (`submit_move`)

A single ADK tool handles all game logic:

```python
def submit_move(user_move: str) -> dict:
    """
    - Validates the move (including bomb restrictions).
    - Generates the bot's move.
    - Resolves the round.
    - Updates game state.
    - Returns structured result for the agent.
    """
```

**Why one tool?**  
The game is simple enough that a single atomic "play a turn" tool keeps the agent's job clear: extract the user's intent and call the tool. The tool returns everything the agent needs to announce the result.

### Agent/Referee

The Gemini model is configured with:
- **System Instruction**: Defines the referee persona (fair, concise, enthusiastic).
- **Tool Binding**: The `submit_move` function is exposed to the model.

**Separation of Concerns:**
1. **Intent Understanding**: The LLM parses user input ("I'll go with rock", "BOMB!") and extracts the move.
2. **Game Logic**: The `submit_move` tool validates, resolves, and mutates state.
3. **Response Generation**: The LLM receives structured results and generates a human-friendly announcement.

---

## Tradeoffs

| Decision                          | Rationale                                                                 |
|-----------------------------------|---------------------------------------------------------------------------|
| Single tool (`submit_move`)       | Simplicity; the game is small. Separate `validate` + `resolve` adds overhead. |
| Global `game_state`               | Avoids passing state through messages; clean for a CLI demo.              |
| Bot uses random moves             | Simple, unpredictable. Could be smarter (e.g., counter-strategy).         |
| "Invalid = wasted round"          | Per spec. Alternative: prompt again (but spec says "wastes the round").   |

---

## What I Would Improve

1. **Multiple Agents**: A "Judge" agent that only interprets moves + a "Rules Engine" agent for pure logic.
2. **Structured Output Schema**: Force the model to return JSON with move, confidence, etc.
3. **Unit Tests**: Pytest suite for `GameState` logic (especially edge cases like double-bomb).
4. **Session Persistence**: Allow resuming a game (serialize state to JSON).
5. **Richer Bot Strategy**: Use a simple ML model or pattern recognition.

---

## File Structure

```
uppliance/
├── referee.py   # Main game: state, tool, agent, CLI loop
└── README.md    # This file
```

---

## Example Session

```
============================================================
  ROCK-PAPER-SCISSORS-PLUS
============================================================

🎯 Referee: Welcome! Here are the rules:
1. Best of 3 rounds (first to 2 wins).
2. Moves: rock, paper, scissors, bomb.
3. Bomb beats all (once per player). Bomb vs bomb = draw.
4. Invalid moves waste the round.
Ready? Enter your move!

Your move: rock

🎯 Referee: Round 1: You played ROCK, I played SCISSORS.
USER wins this round! Score: User 1 - Bot 0.

Your move: bomb

🎯 Referee: Round 2: You played BOMB, I played PAPER.
USER wins this round! 🎉 USER WINS THE GAME!

============================================================
  FINAL: 🎉 USER WINS THE GAME!
  Score: User 2 - 0 Bot
============================================================
```
