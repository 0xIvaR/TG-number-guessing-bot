# Telegram Number Guessing Game Bot

## Development Setup

### Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the project root:
```
BOT_TOKEN=your_telegram_bot_token_here
```

### Running the Bot
```bash
# Run directly
python main.py

# Or using the module
python -m src.bot.telegram_bot
```

### Project Structure
```
telegram-number-guessing-bot/
├── src/                    # Source code
│   ├── bot/               # Bot handlers and main application
│   ├── config/            # Configuration settings
│   ├── database/          # Database operations
│   └── game/              # Game logic
├── data/                  # Database and data files
├── docs/                  # Documentation
├── main.py               # Entry point
├── setup.py              # Package setup
└── requirements.txt      # Dependencies
```

### Testing
The bot includes comprehensive error handling and logging. Check the console output for any issues.

### Deployment
For production deployment, consider:
- Using environment variables for sensitive data
- Setting up proper logging
- Using a process manager like systemd or PM2
- Setting up database backups
