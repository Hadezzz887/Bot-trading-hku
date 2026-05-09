#!/usr/bin/env python3
"""
Database manager for storing trading data, signals, and performance metrics.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database for trading bot."""
    
    def __init__(self, db_path: str = "data/trading_bot.db"):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self.init_db()
    
    def init_db(self):
        """Initialize database tables."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            cursor = self.connection.cursor()
            
            # Trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    symbol TEXT,
                    signal_score REAL,
                    entry_price REAL,
                    exit_price REAL,
                    position_size REAL,
                    pnl REAL,
                    return_pct REAL,
                    status TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Signals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    symbol TEXT,
                    smart_money_signal REAL,
                    news_signal REAL,
                    twitter_signal REAL,
                    combined_signal REAL,
                    confidence REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE,
                    total_trades INTEGER,
                    win_rate REAL,
                    daily_pnl REAL,
                    sharpe_ratio REAL,
                    max_drawdown REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Market data cache
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    symbol TEXT,
                    price REAL,
                    volume REAL,
                    market_cap REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # News data cache
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    title TEXT,
                    source TEXT,
                    sentiment REAL,
                    relevance REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Twitter trends cache
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS twitter_trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    trend_text TEXT,
                    tweet_volume INTEGER,
                    sentiment REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.connection.commit()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def save_trade(self, trade: Dict) -> int:
        """Save a trade to the database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO trades 
                (timestamp, symbol, signal_score, entry_price, exit_price, 
                 position_size, pnl, return_pct, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade.get('timestamp'),
                trade.get('symbol'),
                trade.get('signal_score'),
                trade.get('entry_price'),
                trade.get('exit_price'),
                trade.get('position_size'),
                trade.get('pnl'),
                trade.get('return_pct'),
                trade.get('status', 'open')
            ))
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving trade: {e}")
            return None
    
    def save_signal(self, signal: Dict) -> int:
        """Save a trading signal to the database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO signals 
                (timestamp, symbol, smart_money_signal, news_signal, twitter_signal, 
                 combined_signal, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.get('timestamp'),
                signal.get('symbol'),
                signal.get('smart_money_signal'),
                signal.get('news_signal'),
                signal.get('twitter_signal'),
                signal.get('combined_signal'),
                signal.get('confidence')
            ))
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving signal: {e}")
            return None
    
    def save_performance_metrics(self, metrics: Dict) -> int:
        """Save performance metrics to the database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO performance 
                (date, total_trades, win_rate, daily_pnl, sharpe_ratio, max_drawdown)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                metrics.get('date'),
                metrics.get('total_trades'),
                metrics.get('win_rate'),
                metrics.get('daily_pnl'),
                metrics.get('sharpe_ratio'),
                metrics.get('max_drawdown')
            ))
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving performance metrics: {e}")
            return None
    
    def get_trades(self, limit: int = 100) -> List[Dict]:
        """Retrieve recent trades from database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT id, timestamp, symbol, signal_score, entry_price, exit_price,
                       position_size, pnl, return_pct, status
                FROM trades
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            columns = [description[0] for description in cursor.description]
            trades = []
            for row in cursor.fetchall():
                trades.append(dict(zip(columns, row)))
            return trades
        except Exception as e:
            logger.error(f"Error retrieving trades: {e}")
            return []
    
    def get_performance_summary(self) -> Dict:
        """Get overall performance summary."""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                    SUM(pnl) as total_pnl,
                    AVG(return_pct) as avg_return,
                    MAX(return_pct) as max_return,
                    MIN(return_pct) as min_return
                FROM trades
            ''')
            
            result = cursor.fetchone()
            if result:
                return {
                    'total_trades': result[0] or 0,
                    'winning_trades': result[1] or 0,
                    'losing_trades': result[2] or 0,
                    'total_pnl': result[3] or 0,
                    'avg_return': result[4] or 0,
                    'max_return': result[5] or 0,
                    'min_return': result[6] or 0
                }
            return {}
        except Exception as e:
            logger.error(f"Error retrieving performance summary: {e}")
            return {}
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")


if __name__ == "__main__":
    db = DatabaseManager()
    print("Database manager initialized successfully")
    db.close()
