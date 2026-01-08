"""
Rock-Paper-Scissors-Plus Game Referee
Uses Google Generative AI SDK (ADK) with function calling.
"""

import os
import random
from google import genai
from google.genai import types


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
            self.result_message = "🎉 USER WINS THE GAME!"
        elif self.bot_score >= 2:
            self.game_over = True
            self.result_message = "🤖 BOT WINS THE GAME!"
        elif self.round_number >= 3:
            self.game_over = True
            if self.user_score > self.bot_score:
                self.result_message = "🎉 USER WINS THE GAME!"
            elif self.bot_score > self.user_score:
                self.result_message = "🤖 BOT WINS THE GAME!"
            else:
                self.result_message = "🤝 IT'S A DRAW!"

    def get_status(self) -> str:
        """Return a formatted status string."""
        return (
            f"Round: {self.round_number}/3 | "
            f"Score - User: {self.user_score}, Bot: {self.bot_score} | "
            f"Bomb Available - User: {'Yes' if not self.user_bomb_used else 'No'}, "
            f"Bot: {'Yes' if not self.bot_bomb_used else 'No'}"
        )


# =============================================================================
# GLOBAL GAME STATE INSTANCE
# =============================================================================

game_state = GameState()


# =============================================================================
# ADK TOOL: submit_move
# =============================================================================

def submit_move(user_move: str) -> dict:
    """
    Process the user's move for the current round.

    Args:
        user_move: The move submitted by the user (rock, paper, scissors, bomb).

    Returns:
        A dictionary with round outcome, moves, scores, and game status.
    """
    global game_state

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
            "message": f"Invalid move '{user_move}'! This round is wasted. No points awarded.",
            "round_number": game_state.round_number,
            "user_move": user_move,
            "bot_move": None,
            "round_winner": None,
            "user_score": game_state.user_score,
            "bot_score": game_state.bot_score,
            "game_over": game_state.game_over,
            "final_result": game_state.result_message if game_state.game_over else None,
            "status": game_state.get_status(),
        }

    # Check bomb validity for user
    if user_move == "bomb" and not game_state.can_use_bomb("user"):
        # Bomb already used, treat as invalid
        game_state.round_number += 1
        game_state.check_game_over()
        return {
            "success": False,
            "message": "You already used your bomb! This round is wasted.",
            "round_number": game_state.round_number,
            "user_move": user_move,
            "bot_move": None,
            "round_winner": None,
            "user_score": game_state.user_score,
            "bot_score": game_state.bot_score,
            "game_over": game_state.game_over,
            "final_result": game_state.result_message if game_state.game_over else None,
            "status": game_state.get_status(),
        }

    # Mark bomb used if applicable
    if user_move == "bomb":
        game_state.mark_bomb_used("user")

    # Bot makes a move
    bot_options = ["rock", "paper", "scissors"]
    if game_state.can_use_bomb("bot"):
        # Bot has a small chance to use bomb
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
        round_result = "USER wins this round!"
    elif winner == "bot":
        game_state.bot_score += 1
        round_result = "BOT wins this round!"
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
        "status": game_state.get_status(),
    }


# =============================================================================
# AGENT CONFIGURATION
# =============================================================================

SYSTEM_INSTRUCTION = """You are a fair and enthusiastic referee for Rock-Paper-Scissors-Plus.

RULES (explain briefly when asked or at game start):
1. Best of 3 rounds (first to 2 wins, or most points after 3 rounds).
2. Valid moves: rock, paper, scissors, bomb.
3. Bomb beats everything except another bomb (draw). Each player can use bomb ONCE.
4. Invalid input wastes the round (no points, round counts).
5. Game ends automatically after max 3 rounds.

YOUR JOB:
- Prompt the user for their move.
- Use the `submit_move` tool to process their input.
- Announce the round outcome clearly: Round #, both moves, winner.
- Track and display the score.
- End the game and declare the final result when it's over.

Be concise, enthusiastic, and fair!"""


# =============================================================================
# MAIN GAME LOOP
# =============================================================================

def main():
    """Run the Rock-Paper-Scissors-Plus game in a CLI loop."""
    # Get API key from environment
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY environment variable is not set.")
        print("Please set it with: $env:GOOGLE_API_KEY = 'your-api-key'")
        return

    # Initialize the Gemini client with API key
    client = genai.Client(api_key=api_key)

    # Define the tool for the model
    submit_move_tool = types.Tool(

        function_declarations=[
            types.FunctionDeclaration(
                name="submit_move",
                description="Process the user's move for the current round of Rock-Paper-Scissors-Plus.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "user_move": types.Schema(
                            type=types.Type.STRING,
                            description="The move submitted by the user: rock, paper, scissors, or bomb.",
                        ),
                    },
                    required=["user_move"],
                ),
            )
        ]
    )

    # Create a chat session with the tool
    chat = client.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[submit_move_tool],
        ),
    )

    print("=" * 60)
    print("  ROCK-PAPER-SCISSORS-PLUS  ")
    print("=" * 60)

    # Initial prompt to get the game started
    response = chat.send_message("Start the game! Explain the rules briefly and ask for my first move.")

    while True:
        # Process any function calls in the response
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    # Execute the tool
                    func_name = part.function_call.name
                    func_args = dict(part.function_call.args) if part.function_call.args else {}

                    if func_name == "submit_move":
                        result = submit_move(**func_args)
                        # Send the result back to the model
                        response = chat.send_message(
                            types.Content(
                                parts=[
                                    types.Part(
                                        function_response=types.FunctionResponse(
                                            name=func_name,
                                            response=result,
                                        )
                                    )
                                ]
                            )
                        )
                        continue

            # Print the text response from the model
            text_parts = [p.text for p in response.candidates[0].content.parts if hasattr(p, 'text') and p.text]
            if text_parts:
                print(f"\n🎯 Referee: {''.join(text_parts)}\n")

        # Check if game is over
        if game_state.game_over:
            print("=" * 60)
            print(f"  FINAL: {game_state.result_message}")
            print(f"  Score: User {game_state.user_score} - {game_state.bot_score} Bot")
            print("=" * 60)
            break

        # Get user input
        try:
            user_input = input("Your move: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Thanks for playing! Goodbye!")
                break
        except (KeyboardInterrupt, EOFError):
            print("\nThanks for playing! Goodbye!")
            break

        # Send user input to the model
        response = chat.send_message(user_input)


if __name__ == "__main__":
    main()
