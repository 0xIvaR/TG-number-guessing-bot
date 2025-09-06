"""
Telegram Number Guessing Game Bot

A simple entry point to run the bot application.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.bot.telegram_bot import main

if __name__ == "__main__":
    asyncio.run(main())
