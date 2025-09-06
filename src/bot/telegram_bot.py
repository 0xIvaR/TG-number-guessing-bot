import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode

from ..config.settings import BOT_TOKEN, CATEGORIES, MIN_BET
from ..database.db_manager import GameDatabase
from ..game.game_logic import NumberGuessingGame

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramGameBot:
    def __init__(self):
        self.db = GameDatabase()
        self.game = NumberGuessingGame(self.db)
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Set up all command and message handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("play", self.play_command))
        self.application.add_handler(CommandHandler("balance", self.balance_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("leaderboard", self.leaderboard_command))
        self.application.add_handler(CommandHandler("reset", self.reset_command))
        
        # Callback query handler for inline buttons
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handler for game inputs
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def setup_bot_commands(self):
        """Set up the bot command menu."""
        commands = [
            BotCommand("start", "🎮 Start the bot"),
            BotCommand("play", "🎯 Start a new game"),
            BotCommand("balance", "💰 Check your credits"),
            BotCommand("stats", "📊 View your statistics"),
            BotCommand("leaderboard", "🏆 See top players"),
            BotCommand("reset", "🔄 Reset credits to 10,000"),
            BotCommand("help", "❓ Show help information"),
        ]
        await self.application.bot.set_my_commands(commands)
        logger.info("Bot commands menu set up successfully")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        await self.db.get_user(user.id, user.username)
        
        welcome_message = f"🎮 **Welcome to Number Guessing Game, {user.first_name}!**\n\n"
        welcome_message += "You start with 10,000 credits! Try your luck in our exciting number guessing game.\n\n"
        welcome_message += self.game.get_categories_info()
        welcome_message += "💡 **Tip:** Click the menu button (☰) next to the text input or type `/` to see all available commands!"
        
        # Create buttons for Play and Help
        keyboard = [
            [InlineKeyboardButton("🎯 Play Game", callback_data="start_play")],
            [InlineKeyboardButton("❓ Help", callback_data="start_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = self.game.get_game_help()
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def play_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /play command - show category selection."""
        user = update.effective_user
        user_data = await self.db.get_user(user.id, user.username)
        
        if user_data['credits'] <= 0:
            await update.message.reply_text(
                "😞 You don't have any credits left! Contact the administrator to get more credits.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        keyboard = []
        for category_id, category in CATEGORIES.items():
            button_text = f"{category['emoji']} {category['name']} ({category['multiplier']}x)"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"category_{category_id}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"🎮 **Choose Your Game Category**\n\n"
        message += f"💳 **Your Credits:** {user_data['credits']}\n\n"
        message += "Select a category to start playing:"
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /balance command."""
        user = update.effective_user
        user_data = await self.db.get_user(user.id, user.username)
        
        message = f"💳 **Your Balance**\n\n"
        message += f"💰 **Credits:** {user_data['credits']}\n"
        message += f"🎮 **Games Played:** {user_data['games_played']}\n"
        message += f"🏆 **Games Won:** {user_data['games_won']}"
        
        if user_data['games_played'] > 0:
            win_rate = (user_data['games_won'] / user_data['games_played']) * 100
            message += f"\n📊 **Win Rate:** {win_rate:.1f}%"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command."""
        user = update.effective_user
        stats = await self.db.get_user_stats(user.id)
        
        if not stats:
            await update.message.reply_text("No statistics available yet. Play some games first!")
            return
        
        credits, games_played, games_won, total_wagered, total_winnings = stats
        
        message = f"📊 **Your Statistics**\n\n"
        message += f"💰 **Current Credits:** {credits}\n"
        message += f"🎮 **Games Played:** {games_played}\n"
        message += f"🏆 **Games Won:** {games_won}\n"
        message += f"💸 **Total Wagered:** {total_wagered}\n"
        message += f"💎 **Total Winnings:** {total_winnings}\n"
        
        if games_played > 0:
            win_rate = (games_won / games_played) * 100
            message += f"📈 **Win Rate:** {win_rate:.1f}%\n"
            
            net_profit = total_winnings - total_wagered
            message += f"📊 **Net Profit:** {net_profit:+d} credits"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def leaderboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /leaderboard command."""
        leaderboard = await self.db.get_leaderboard()
        
        if not leaderboard:
            await update.message.reply_text("No players on the leaderboard yet!")
            return
        
        message = "🏆 **Top Players (by Credits)**\n\n"
        
        for i, (username, credits, games_played, games_won) in enumerate(leaderboard, 1):
            trophy = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            
            win_rate = (games_won / games_played * 100) if games_played > 0 else 0
            username_display = username or "Anonymous"
            
            message += f"{trophy} **{username_display}**\n"
            message += f"   💰 {credits} credits | 🎮 {games_played} games | 📈 {win_rate:.1f}% win rate\n\n"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks."""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        data = query.data
        
        if data.startswith("category_"):
            category = data.replace("category_", "")
            await self.handle_category_selection(query, user, category)
        elif data.startswith("bet_"):
            parts = data.split("_")
            category = parts[1]
            bet_amount = int(parts[2])
            await self.handle_bet_selection(query, user, category, bet_amount)
        elif data.startswith("custom_bet_"):
            category = data.replace("custom_bet_", "")
            await self.handle_custom_bet_selection(query, user, category)
        elif data.startswith("play_again_"):
            category = data.replace("play_again_", "")
            await self.handle_play_again(query, user, category)
        elif data == "start_play":
            await self.handle_start_play_button(query, user)
        elif data == "start_help":
            await self.handle_start_help_button(query, user)
    
    async def handle_category_selection(self, query, user, category):
        """Handle category selection."""
        user_data = await self.db.get_user(user.id, user.username)
        category_info = CATEGORIES[category]
        
        # Create bet amount buttons
        suggested_bets = [10, 25, 50, 100]
        keyboard = []
        
        for bet in suggested_bets:
            if bet <= user_data['credits']:
                keyboard.append([InlineKeyboardButton(f"{bet} credits", callback_data=f"bet_{category}_{bet}")])
        
        # Add custom bet option
        keyboard.append([InlineKeyboardButton("💭 Custom Amount", callback_data=f"custom_bet_{category}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"🎯 **{category_info['emoji']} {category_info['name']} Selected**\n\n"
        message += f"📊 **Range:** {category_info['range'][0]}-{category_info['range'][1]}\n"
        message += f"💎 **Win Multiplier:** {category_info['multiplier']}x\n"
        message += f"💰 **Your Credits:** {user_data['credits']}\n\n"
        message += "Choose your bet amount:"
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_bet_selection(self, query, user, category, bet_amount):
        """Handle bet amount selection."""
        user_data = await self.db.get_user(user.id, user.username)
        
        # Validate bet
        is_valid, message = self.game.validate_bet(user_data['credits'], bet_amount, category)
        if not is_valid:
            await query.edit_message_text(f"❌ {message}", parse_mode=ParseMode.MARKDOWN)
            return
        
        # Start game session
        self.game.start_game_session(user.id, category, bet_amount)
        
        category_info = CATEGORIES[category]
        min_num, max_num = category_info['range']
        
        message = f"🎮 **Game Started!**\n\n"
        message += f"🎯 **Category:** {category_info['emoji']} {category_info['name']}\n"
        message += f"💰 **Bet Amount:** {bet_amount} credits\n"
        message += f"🎲 **Multiplier:** {category_info['multiplier']}x\n\n"
        message += f"🔢 **Choose a number between {min_num} and {max_num}:**\n"
        message += "Type your guess in the chat!"
        
        await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_custom_bet_selection(self, query, user, category):
        """Handle custom bet amount selection."""
        category_info = CATEGORIES[category]
        user_data = await self.db.get_user(user.id, user.username)
        
        message = f"💭 **Custom Bet Amount**\n\n"
        message += f"🎯 **Category:** {category_info['emoji']} {category_info['name']}\n"
        message += f"💰 **Your Credits:** {user_data['credits']}\n"
        message += f"📊 **Range:** {category_info['range'][0]}-{category_info['range'][1]}\n"
        message += f"💎 **Win Multiplier:** {category_info['multiplier']}x\n\n"
        message += f"Please type your custom bet amount (minimum {MIN_BET}, maximum {user_data['credits']}):"
        
        # Store the category in user session for custom bet
        self.game.user_sessions[user.id] = {
            'stage': 'waiting_for_custom_bet',
            'category': category
        }
        
        await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_play_again(self, query, user, category):
        """Handle play again button - go back to bet selection."""
        user_data = await self.db.get_user(user.id, user.username)
        
        if user_data['credits'] <= 0:
            await query.edit_message_text(
                "😞 You don't have any credits left! Use `/reset` to get 10,000 credits.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Reuse the category selection logic
        await self.handle_category_selection(query, user, category)
    
    async def handle_start_play_button(self, query, user):
        """Handle the Play Game button from start message."""
        user_data = await self.db.get_user(user.id, user.username)
        
        if user_data['credits'] <= 0:
            await query.edit_message_text(
                "😞 You don't have any credits left! Use `/reset` to get 10,000 credits.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        keyboard = []
        for category_id, category in CATEGORIES.items():
            button_text = f"{category['emoji']} {category['name']} ({category['multiplier']}x)"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"category_{category_id}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"🎮 **Choose Your Game Category**\n\n"
        message += f"💳 **Your Credits:** {user_data['credits']}\n\n"
        message += "Select a category to start playing:"
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_start_help_button(self, query, user):
        """Handle the Help button from start message."""
        help_text = self.game.get_game_help()
        await query.edit_message_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (mainly for game guesses and custom bet amounts)."""
        user = update.effective_user
        session = self.game.get_user_session(user.id)
        
        if not session:
            await update.message.reply_text(
                "No active game session. Use `/play` to start a new game!",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Handle custom bet amount input
        if session.get('stage') == 'waiting_for_custom_bet':
            try:
                bet_amount = int(update.message.text.strip())
                category = session['category']
                
                user_data = await self.db.get_user(user.id, user.username)
                
                # Validate bet
                is_valid, message = self.game.validate_bet(user_data['credits'], bet_amount, category)
                if not is_valid:
                    await update.message.reply_text(f"❌ {message}\nPlease enter a valid amount:", parse_mode=ParseMode.MARKDOWN)
                    return
                
                # Start game session
                self.game.start_game_session(user.id, category, bet_amount)
                
                category_info = CATEGORIES[category]
                min_num, max_num = category_info['range']
                
                game_message = f"🎮 **Game Started!**\n\n"
                game_message += f"🎯 **Category:** {category_info['emoji']} {category_info['name']}\n"
                game_message += f"💰 **Bet Amount:** {bet_amount} credits\n"
                game_message += f"🎲 **Multiplier:** {category_info['multiplier']}x\n\n"
                game_message += f"🔢 **Choose a number between {min_num} and {max_num}:**\n"
                game_message += "Type your guess in the chat!"
                
                await update.message.reply_text(game_message, parse_mode=ParseMode.MARKDOWN)
                
            except ValueError:
                await update.message.reply_text(
                    "Please enter a valid number for your bet amount!",
                    parse_mode=ParseMode.MARKDOWN
                )
            return
        
        # Handle game guess input
        if session.get('stage') == 'waiting_for_guess':
            try:
                guess = int(update.message.text.strip())
            except ValueError:
                await update.message.reply_text(
                    "Please enter a valid number!",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Play the game
            result, message = await self.game.play_game(user.id, guess)
            
            if result is None:
                await update.message.reply_text(f"❌ {message}", parse_mode=ParseMode.MARKDOWN)
                return
            
            # Send game result with play again button
            result_message = self.game.format_game_result(result)
            
            # Add play again button
            keyboard = [[InlineKeyboardButton(f"🎯 Play Again ({result['category_info']['emoji']} {result['category_info']['name']})", 
                                             callback_data=f"play_again_{result['category']}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(result_message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            
            # If user has no credits left, show game over message
            if result['new_credits'] <= 0:
                await update.message.reply_text(
                    "💀 **Game Over!** You've run out of credits!\n\n"
                    "Use `/reset` to get 10,000 credits and continue playing.",
                    parse_mode=ParseMode.MARKDOWN
                )
            return
        
        # Default case - no valid session stage
        await update.message.reply_text(
            "I don't understand. Use `/play` to start a new game!",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def reset_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /reset command - reset user credits to 10,000."""
        user = update.effective_user
        
        # Reset credits to 10,000
        await self.db.update_credits(user.id, 10000)
        
        message = f"🔄 **Credits Reset!**\n\n"
        message += f"✅ Your credits have been reset to 10,000!\n"
        message += f"💰 **New Balance:** 10,000 credits\n\n"
        message += f"Ready to play again? Use `/play` to start a new game!"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def start_bot(self):
        """Start the bot."""
        await self.db.init_db()
        logger.info("Starting bot...")
        await self.application.initialize()
        await self.setup_bot_commands()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info("Bot started successfully!")
    
    async def stop_bot(self):
        """Stop the bot."""
        logger.info("Stopping bot...")
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()
        logger.info("Bot stopped.")

async def main():
    """Main function to run the bot."""
    bot = TelegramGameBot()
    
    try:
        await bot.start_bot()
        # Keep the bot running
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await bot.stop_bot()

if __name__ == "__main__":
    asyncio.run(main()) 
