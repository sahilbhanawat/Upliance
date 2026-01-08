"""
Rock-Paper-Scissors-Plus Game Referee
A CLI game where you play against a bot referee.
Uses ADK-style tools for game logic separation.
"""

import random


# =============================================================================
# GAME STATE MODEL
# =============================================================================

class GameState:
    """
    Manages the state of a Rock-Paper-Scissors-Plus game.
    - Tracks round number, scores, and bomb usage for both players.
    - Provides validation and resolution logic.
    """

    VALID_MOVES = {"rock", "paper", "scissors", "bomb"}
    BEATS = {
        "rock": "scissors",
        "paper": "rock",
        "scissors": "paper",
    }

    def __init__(self):
        self.round_number = 0
        self.user_score = 0
        self.bot_score = 0
        self.user_bomb_used = False
        self.bot_bomb_used = False
        self.game_over = False
        self.result_message = ""

    def is_valid_move(self, move: str) -> bool:
        """Check if the move is one of rock, paper, scissors, bomb."""
        return move.lower().strip() in self.VALID_MOVES

    def can_use_bomb(self, player: str) -> bool:
        """Check if the player can still use bomb."""
        if player == "user":
            return not self.user_bomb_used
        return not self.bot_bomb_used

    def mark_bomb_used(self, player: str):
        """Mark that a player has used their bomb."""
        if player == "user":
            self.user_bomb_used = True
        else:
            self.bot_bomb_used = True

    def resolve(self, user_move: str, bot_move: str) -> str:
        """
        Determine the winner of a round.
        Returns: 'user', 'bot', or 'draw'.
        """
        if user_move == bot_move:
            return "draw"

        # Bomb logic
        if user_move == "bomb" and bot_move == "bomb":
            return "draw"
        if user_move == "bomb":
            return "user"
        if bot_move == "bomb":
            return "bot"

        # Standard RPS logic
        if self.BEATS.get(user_move) == bot_move:
            return "user"
        return "bot"

    def check_game_over(self):
        """
        Check if the game should end:
        - Best of 3: first to 2 wins, OR
        - Max 3 rounds played.
        """
        if self.user_score >= 2:
            self.game_over = True
            self.result_message = "🎉 YOU WIN THE GAME!"
        elif self.bot_score >= 2:
            self.game_over = True
            self.result_message = "🤖 BOT WINS THE GAME!"
        elif self.round_number >= 3:
            self.game_over = True
            if self.user_score > self.bot_score:
                self.result_message = "🎉 YOU WIN THE GAME!"
            elif self.bot_score > self.user_score:
                self.result_message = "🤖 BOT WINS THE GAME!"
            else:
                self.result_message = "🤝 IT'S A DRAW!"

    def get_status(self) -> str:
        """Return a formatted status string."""
        return (
            f"Score - You: {self.user_score}, Bot: {self.bot_score} | "
            f"Bomb left - You: {'Yes' if not self.user_bomb_used else 'No'}, "
            f"Bot: {'Yes' if not self.bot_bomb_used else 'No'}"
        )


# =============================================================================
# ADK TOOL: submit_move (game logic separated from interface)
# =============================================================================

def submit_move(game_state: GameState, user_move: str) -> dict:
    """
    Process the user's move for the current round.
    This is the ADK-style tool that handles all game logic.

    Args:
        game_state: The current game state object.
        user_move: The move submitted by the user.

    Returns:
        A dictionary with round outcome, moves, scores, and game status.
    """
    # Check if game is already over
    if game_state.game_over:
        return {
            "success": False,
            "message": "The game is already over! " + game_state.result_message,
            "game_over": True,
            "final_result": game_state.result_message,
        }

    # Normalize move
    user_move = user_move.lower().strip()

    # Validate move
    if not game_state.is_valid_move(user_move):
        # Invalid move wastes the round
        game_state.round_number += 1
        game_state.check_game_over()
        return {
            "success": False,
            "message": f"Invalid move '{user_move}'! Round wasted. No points awarded.",
            "round_number": game_state.round_number,
            "user_move": user_move,
            "bot_move": None,
            "round_winner": None,
            "user_score": game_state.user_score,
            "bot_score": game_state.bot_score,
            "game_over": game_state.game_over,
            "final_result": game_state.result_message if game_state.game_over else None,
        }

    # Check bomb validity for user
    if user_move == "bomb" and not game_state.can_use_bomb("user"):
        game_state.round_number += 1
        game_state.check_game_over()
        return {
            "success": False,
            "message": "You already used your bomb! Round wasted.",
            "round_number": game_state.round_number,
            "user_move": user_move,
            "bot_move": None,
            "round_winner": None,
            "user_score": game_state.user_score,
            "bot_score": game_state.bot_score,
            "game_over": game_state.game_over,
            "final_result": game_state.result_message if game_state.game_over else None,
        }

    # Mark bomb used if applicable
    if user_move == "bomb":
        game_state.mark_bomb_used("user")

    # Bot makes a move (simple AI)
    bot_options = ["rock", "paper", "scissors"]
    if game_state.can_use_bomb("bot"):
        # Bot has 20% chance to use bomb if available
        if random.random() < 0.2:
            bot_options.append("bomb")
    bot_move = random.choice(bot_options)

    if bot_move == "bomb":
        game_state.mark_bomb_used("bot")

    # Increment round
    game_state.round_number += 1

    # Resolve the round
    winner = game_state.resolve(user_move, bot_move)
    if winner == "user":
        game_state.user_score += 1
        round_result = "You WIN this round!"
    elif winner == "bot":
        game_state.bot_score += 1
        round_result = "Bot WINS this round!"
    else:
        round_result = "It's a DRAW!"

    # Check for game over
    game_state.check_game_over()

    return {
        "success": True,
        "message": round_result,
        "round_number": game_state.round_number,
        "user_move": user_move,
        "bot_move": bot_move,
        "round_winner": winner,
        "user_score": game_state.user_score,
        "bot_score": game_state.bot_score,
        "game_over": game_state.game_over,
        "final_result": game_state.result_message if game_state.game_over else None,
    }


# =============================================================================
# RESPONSE GENERATION (separated from game logic)
# =============================================================================

def format_round_result(result: dict) -> str:
    """Generate a human-readable response from the tool result."""
    lines = []
    
    if not result["success"] and result.get("bot_move") is None:
        # Invalid move or bomb reuse
        lines.append(f"❌ {result['message']}")
    else:
        # Valid round played
        lines.append(f"🎮 Round {result['round_number']}")
        lines.append(f"   You: {result['user_move'].upper()}  vs  Bot: {result['bot_move'].upper()}")
        lines.append(f"   ➡️  {result['message']}")
    
    lines.append(f"   📊 Score: You {result['user_score']} - {result['bot_score']} Bot")
    
    if result["game_over"]:
        lines.append("")
        lines.append("=" * 50)
        lines.append(f"   {result['final_result']}")
        lines.append("=" * 50)
    
    return "\n".join(lines)


# =============================================================================
# MAIN GAME LOOP (Intent Understanding + Interface)
# =============================================================================

def print_rules():
    """Print the game rules (max 5 lines as per spec)."""
    print("""
📋 RULES:
1. Best of 3 rounds (first to 2 wins)
2. Moves: rock, paper, scissors, bomb
3. Bomb beats all (once per player). Bomb vs bomb = draw.
4. Invalid input wastes the round.
5. Game ends after max 3 rounds.
""")


def main():
    """Run the Rock-Paper-Scissors-Plus game."""
    print("=" * 50)
    print("   🎯 ROCK-PAPER-SCISSORS-PLUS 🎯")
    print("=" * 50)
    
    print_rules()
    
    # Initialize game state
    game = GameState()
    
    print(f"🎮 {game.get_status()}")
    print("-" * 50)
    
    while not game.game_over:
        # Get user input (Intent Understanding)
        try:
            user_input = input(f"Round {game.round_number + 1} - Your move: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Thanks for playing! Goodbye!")
                return
        except (KeyboardInterrupt, EOFError):
            print("\nThanks for playing! Goodbye!")
            return
        
        # Process move through the tool (Game Logic)
        result = submit_move(game, user_input)
        
        # Generate and display response (Response Generation)
        print()
        print(format_round_result(result))
        print()
        
        if not game.game_over:
            print(f"🎮 {game.get_status()}")
            print("-" * 50)
    
    print("\n🎮 Thanks for playing!")


if __name__ == "__main__":
    main()
