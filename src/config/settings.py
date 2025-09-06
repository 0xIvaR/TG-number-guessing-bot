# Configuration file for Telegram bot
import os

# Bot Token - Replace with your actual bot token from @BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN', '7112631389:AAGHH8YR-sUtqZXnI2nXZ6lfC2seB62J8kk')

# Game Configuration
INITIAL_CREDITS = 10000
MIN_BET = 1

# Categories Configuration
CATEGORIES = {
    'easy': {
        'name': '1-10 Range',
        'range': (1, 10),
        'multiplier': 2,
        'emoji': '🟢'
    },
    'medium': {
        'name': '1-100 Range', 
        'range': (1, 100),
        'multiplier': 4,
        'emoji': '🟡'
    },
    'hard': {
        'name': '1-1000 Range',
        'range': (1, 1000),
        'multiplier': 8,
        'emoji': '🔴'
    }
}

# Database Configuration
DATABASE_PATH = 'data/game_bot.db' 
