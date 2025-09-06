import aiosqlite
import logging
from ..config.settings import DATABASE_PATH, INITIAL_CREDITS

logger = logging.getLogger(__name__)

class GameDatabase:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
    
    async def init_db(self):
        """Initialize the database and create tables if they don't exist."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f'''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    credits INTEGER DEFAULT {INITIAL_CREDITS},
                    games_played INTEGER DEFAULT 0,
                    games_won INTEGER DEFAULT 0,
                    total_wagered INTEGER DEFAULT 0,
                    total_winnings INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS game_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    category TEXT,
                    bet_amount INTEGER,
                    guessed_number INTEGER,
                    winning_number INTEGER,
                    won BOOLEAN,
                    payout INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            await db.commit()
            logger.info("Database initialized successfully")
    
    async def get_user(self, user_id: int, username: str = None):
        """Get user data or create new user if doesn't exist."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
                user = await cursor.fetchone()
            
            if user is None:
                # Create new user
                await db.execute(
                    'INSERT INTO users (user_id, username, credits) VALUES (?, ?, ?)',
                    (user_id, username, INITIAL_CREDITS)
                )
                await db.commit()
                logger.info(f"Created new user: {user_id} ({username})")
                return {
                    'user_id': user_id,
                    'username': username,
                    'credits': INITIAL_CREDITS,
                    'games_played': 0,
                    'games_won': 0,
                    'total_wagered': 0,
                    'total_winnings': 0
                }
            
            return {
                'user_id': user[0],
                'username': user[1],
                'credits': user[2],
                'games_played': user[3],
                'games_won': user[4],
                'total_wagered': user[5],
                'total_winnings': user[6]
            }
    
    async def update_credits(self, user_id: int, new_credits: int):
        """Update user's credits."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE users SET credits = ? WHERE user_id = ?',
                (new_credits, user_id)
            )
            await db.commit()
    
    async def record_game(self, user_id: int, category: str, bet_amount: int, 
                         guessed_number: int, winning_number: int, won: bool, payout: int):
        """Record a game in the history and update user stats."""
        async with aiosqlite.connect(self.db_path) as db:
            # Record game history
            await db.execute('''
                INSERT INTO game_history 
                (user_id, category, bet_amount, guessed_number, winning_number, won, payout)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, category, bet_amount, guessed_number, winning_number, won, payout))
            
            # Update user stats
            games_won_increment = 1 if won else 0
            total_winnings_increment = payout if won else 0
            
            await db.execute('''
                UPDATE users SET 
                    games_played = games_played + 1,
                    games_won = games_won + ?,
                    total_wagered = total_wagered + ?,
                    total_winnings = total_winnings + ?
                WHERE user_id = ?
            ''', (games_won_increment, bet_amount, total_winnings_increment, user_id))
            
            await db.commit()
    
    async def get_user_stats(self, user_id: int):
        """Get detailed user statistics."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT credits, games_played, games_won, total_wagered, total_winnings
                FROM users WHERE user_id = ?
            ''', (user_id,)) as cursor:
                return await cursor.fetchone()
    
    async def get_leaderboard(self, limit: int = 10):
        """Get top users by credits."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT username, credits, games_played, games_won
                FROM users 
                ORDER BY credits DESC 
                LIMIT ?
            ''', (limit,)) as cursor:
                return await cursor.fetchall() 
