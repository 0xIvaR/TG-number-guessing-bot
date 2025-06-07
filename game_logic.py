import random
import logging
from config import CATEGORIES, MIN_BET

logger = logging.getLogger(__name__)

class NumberGuessingGame:
    def __init__(self, database):
        self.db = database
        self.user_sessions = {}  # Store active game sessions
    
    def get_categories_info(self):
        """Get formatted information about all game categories."""
        info = "🎮 **Game Categories:**\n\n"
        for category_id, category in CATEGORIES.items():
            info += f"{category['emoji']} **{category['name']}**\n"
            info += f"   • Range: {category['range'][0]}-{category['range'][1]}\n"
            info += f"   • Win Multiplier: {category['multiplier']}x\n\n"
        return info
    
    def validate_bet(self, user_credits: int, bet_amount: int, category: str):
        """Validate if the bet is valid."""
        if bet_amount < MIN_BET:
            return False, f"Minimum bet is {MIN_BET} credits!"
        
        if bet_amount > user_credits:
            return False, "You don't have enough credits!"
        
        if category not in CATEGORIES:
            return False, "Invalid category!"
        
        return True, "Valid bet"
    
    def validate_guess(self, guess: int, category: str):
        """Validate if the guess is within the category range."""
        if category not in CATEGORIES:
            return False, "Invalid category!"
        
        min_num, max_num = CATEGORIES[category]['range']
        if guess < min_num or guess > max_num:
            return False, f"Number must be between {min_num} and {max_num}!"
        
        return True, "Valid guess"
    
    def start_game_session(self, user_id: int, category: str, bet_amount: int):
        """Start a new game session for a user."""
        self.user_sessions[user_id] = {
            'category': category,
            'bet_amount': bet_amount,
            'stage': 'waiting_for_guess'
        }
        logger.info(f"Started game session for user {user_id}: {category} with bet {bet_amount}")
    
    def get_user_session(self, user_id: int):
        """Get current game session for a user."""
        return self.user_sessions.get(user_id)
    
    def end_game_session(self, user_id: int):
        """End the game session for a user."""
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
    
    async def play_game(self, user_id: int, guess: int):
        """Execute the game logic and return results."""
        session = self.get_user_session(user_id)
        if not session:
            return None, "No active game session!"
        
        category = session['category']
        bet_amount = session['bet_amount']
        
        # Validate guess
        is_valid, message = self.validate_guess(guess, category)
        if not is_valid:
            return None, message
        
        # Generate winning number
        min_num, max_num = CATEGORIES[category]['range']
        winning_number = random.randint(min_num, max_num)
        
        # Check if user won
        won = (guess == winning_number)
        payout = 0
        
        if won:
            multiplier = CATEGORIES[category]['multiplier']
            payout = bet_amount * multiplier
            
        # Update user credits
        user = await self.db.get_user(user_id)
        new_credits = user['credits'] - bet_amount + payout
        await self.db.update_credits(user_id, new_credits)
        
        # Record the game
        await self.db.record_game(
            user_id, category, bet_amount, guess, winning_number, won, payout
        )
        
        # End session
        self.end_game_session(user_id)
        
        # Prepare result
        result = {
            'won': won,
            'guess': guess,
            'winning_number': winning_number,
            'bet_amount': bet_amount,
            'payout': payout,
            'category': category,
            'new_credits': new_credits,
            'category_info': CATEGORIES[category]
        }
        
        logger.info(f"Game result for user {user_id}: {result}")
        return result, "Game completed"
    
    def format_game_result(self, result):
        """Format the game result into a nice message."""
        if not result:
            return "Error occurred during the game!"
        
        category_info = result['category_info']
        emoji = "🎉" if result['won'] else "😞"
        
        message = f"{emoji} **Game Result**\n\n"
        message += f"🎯 **Category:** {category_info['emoji']} {category_info['name']}\n"
        message += f"🔢 **Your Guess:** {result['guess']}\n"
        message += f"🎲 **Winning Number:** {result['winning_number']}\n"
        message += f"💰 **Bet Amount:** {result['bet_amount']} credits\n\n"
        
        if result['won']:
            message += f"🏆 **YOU WON!**\n"
            message += f"💎 **Payout:** {result['payout']} credits ({category_info['multiplier']}x)\n"
        else:
            message += f"💸 **You Lost!**\n"
            message += f"❌ **Lost:** {result['bet_amount']} credits\n"
        
        message += f"\n💳 **New Balance:** {result['new_credits']} credits"
        
        return message
    
    def get_game_help(self):
        """Get help message for the game."""
        help_text = "🎮 **Number Guessing Game Help**\n\n"
        help_text += "**How to Play:**\n"
        help_text += "1. Choose a category with `/play`\n"
        help_text += "2. Enter your bet amount\n"
        help_text += "3. Guess a number in the range\n"
        help_text += "4. Win credits if you guess correctly!\n\n"
        
        help_text += self.get_categories_info()
        
        help_text += "**Commands:**\n"
        help_text += "• `/start` - Start the bot\n"
        help_text += "• `/play` - Start a new game\n"
        help_text += "• `/balance` - Check your credits\n"
        help_text += "• `/stats` - View your statistics\n"
        help_text += "• `/leaderboard` - Top players\n"
        help_text += "• `/help` - Show this help\n"
        
        return help_text 