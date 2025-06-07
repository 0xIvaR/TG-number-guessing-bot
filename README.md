# 🎮 Telegram Number Guessing Game Bot

A fun and engaging Telegram bot that implements a number guessing game where users can win credits across multiple difficulty levels with different risk-reward ratios.

## 🎯 Game Features

### Game Mechanics
- **Starting Credits**: Every user begins with 10,000 credits
- **Three Categories**:
  - 🟢 **Easy (1-10)**: 2x multiplier - Lower risk, lower reward
  - 🟡 **Medium (1-100)**: 4x multiplier - Medium risk, medium reward  
  - 🔴 **Hard (1-1000)**: 8x multiplier - High risk, high reward
- **Interactive Command Menu**: Click the menu button (☰) next to the text input or type `/` to see all available commands

### How to Play
1. Use `/play` to start a game or click the "Play" button from the command menu
2. Choose your preferred category
3. Select or enter your bet amount (minimum 1 credit)
4. Guess a number within the category range
5. Win credits if your guess matches the randomly generated number!

### Bot Commands
- `/start` - Welcome message and introduction with Play/Help buttons
- `/play` - Start a new game
- `/balance` - Check your current credits and basic stats
- `/stats` - View detailed statistics
- `/leaderboard` - See top players
- `/reset` - Reset your credits to 10,000
- `/help` - Show game instructions

**💡 Tip:** All commands are also available through the interactive command menu - just click the menu button (☰) next to the text input!

### New Features
- **Interactive Start Screen**: Click "Play Game" or "Help" buttons instead of typing commands
- **Custom Bet Amounts**: Choose from suggested amounts or enter your own custom bet
- **Play Again Button**: After each game, quickly play the same category again
- **Credit Reset**: Use `/reset` to restore your credits to 10,000 anytime
- **Enhanced UI**: Beautiful button-based interface for better user experience

## 🛠 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### Installation

1. **Clone this repository**
   ```bash
   git clone https://github.com/yourusername/telegram-number-guessing-bot.git
   cd telegram-number-guessing-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get your Bot Token**
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Create a new bot with `/newbot`
   - Follow the instructions to get your bot token

4. **Configure the bot**
   - Open `config.py`
   - Replace `'YOUR_BOT_TOKEN_HERE'` with your actual bot token
   
   **OR**
   
   - Set environment variable:
   ```bash
   export BOT_TOKEN="your_actual_bot_token_here"
   ```

5. **Run the bot**
   ```bash
   python bot.py
   ```

### Configuration Options

In `config.py`, you can customize:
- `INITIAL_CREDITS`: Starting credits for new users (default: 10,000)
- `MIN_BET`: Minimum bet amount (default: 1)
- Category settings (ranges, multipliers, emojis)

## 📊 Game Statistics

The bot tracks comprehensive statistics:
- Credits balance
- Games played and won
- Win rate percentage
- Total amount wagered
- Total winnings
- Net profit/loss

## 🏆 Leaderboard

Players are ranked by their current credits, creating a competitive environment. The leaderboard shows:
- Player rankings
- Current credits
- Games played
- Win rates

## 🗄 Database

The bot uses SQLite for data persistence:
- User profiles and balances
- Game history
- Statistics tracking
- No external database setup required

## 🎮 Example Gameplay

```
User: /play
Bot: [Shows category selection buttons]

User: [Selects "🟢 1-10 Range (2x)"]
Bot: [Shows bet amount options]

User: [Selects "20 credits"]
Bot: "Game Started! Choose a number between 1 and 10:"

User: 7
Bot: "🎉 YOU WON! Your guess: 7, Winning number: 7
     Payout: 40 credits (2x)
     New Balance: 120 credits"
```

## 🔧 Technical Details

- **Framework**: python-telegram-bot 20.7
- **Database**: SQLite with aiosqlite for async operations
- **Architecture**: Modular design with separate files for database, game logic, and bot handlers
- **Error Handling**: Comprehensive validation and error messages
- **Logging**: Detailed logging for monitoring and debugging

## 🛡 Security Features

- Input validation for all user inputs
- Bet amount validation (can't bet more than available credits)
- Number range validation for guesses
- Session management to prevent cheating

## 📝 File Structure

```
telegram-number-guessing-bot/
├── bot.py              # Main bot application
├── config.py           # Configuration settings
├── database.py         # Database operations
├── game_logic.py       # Core game mechanics
├── requirements.txt    # Python dependencies
├── game_bot.db         # SQLite database (auto-created)
└── README.md          # Project documentation
```

## 🚀 Running the Bot

After setup, users can find your bot on Telegram and start playing immediately. The bot will:
- Automatically create user accounts
- Track all game data
- Provide real-time feedback
- Maintain persistent statistics

## 🎯 Future Enhancements

Potential features to add:
- Daily bonus credits
- Achievement system
- Tournament modes
- Admin commands for credit management
- Multiple language support
- Custom themes

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 📞 Support

If you encounter any issues:
1. Check the console logs for error messages
2. Verify your bot token is correct
3. Ensure all dependencies are installed
4. Check that your bot has the necessary permissions

For questions or suggestions, please open an issue on GitHub.

---

**⭐ If you found this project helpful, please give it a star on GitHub!**

Enjoy your Telegram number guessing game! 🎮🎯 