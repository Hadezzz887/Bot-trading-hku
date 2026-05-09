#!/usr/bin/env python3
"""
Telegram notifications for trading events.
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Optional, Dict
from src.utils.config import Config

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Send Telegram notifications for trading events."""
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or Config.get('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or Config.get('TELEGRAM_CHAT_ID')
        self.enabled = bool(self.bot_token and self.chat_id)
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage" if self.bot_token else None
    
    async def send_trade_signal(self, symbol: str, signal: float, confidence: float, 
                               sources: Dict[str, float]):
        """Send trade signal notification to Telegram."""
        if not self.enabled:
            return
        
        signal_type = "🟢 BUY" if signal > 0 else "🔴 SELL"
        message = f"""
{signal_type} Signal - {symbol}
━━━━━━━━━━━━━━━━━━━━
Signal Strength: {signal:.2f}
Confidence: {confidence*100:.1f}%

Signal Sources:
├─ Smart Money: {sources.get('smart_money', 0):.2f}
├─ News: {sources.get('news', 0):.2f}
└─ Twitter: {sources.get('twitter', 0):.2f}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        await self._send_message(message)
    
    async def send_trade_execution(self, symbol: str, action: str, price: float, 
                                  position_size: float):
        """Send trade execution notification."""
        if not self.enabled:
            return
        
        emoji = "🟢" if action.upper() == "BUY" else "🔴"
        message = f"""
{emoji} Trade Executed
━━━━━━━━━━━━━━━━━━━━
Action: {action.upper()}
Symbol: {symbol}
Price: ${price:.2f}
Position Size: {position_size:.2f}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        await self._send_message(message)
    
    async def send_profit_loss(self, pnl: float, return_pct: float):
        """Send P&L notification."""
        if not self.enabled:
            return
        
        emoji = "📈" if pnl > 0 else "📉"
        message = f"""
{emoji} Trade Closed - P&L
━━━━━━━━━━━━━━━━━━━━
Profit/Loss: ${pnl:.2f}
Return: {return_pct:.2f}%

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        await self._send_message(message)
    
    async def send_error_alert(self, error_type: str, error_message: str):
        """Send error/alert notification."""
        if not self.enabled:
            return
        
        message = f"""
⚠️ Alert - {error_type}
━━━━━━━━━━━━━━━━━━━━
{error_message}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        await self._send_message(message)
    
    async def send_daily_report(self, stats: Dict):
        """Send daily performance report."""
        if not self.enabled:
            return
        
        message = f"""
📊 Daily Performance Report
━━━━━━━━━━━━━━━━━━━━
Total Trades: {stats.get('total_trades', 0)}
Win Rate: {stats.get('win_rate', 0):.1f}%
Daily P&L: ${stats.get('daily_pnl', 0):.2f}
Balance: ${stats.get('balance', 0):.2f}
Sharpe Ratio: {stats.get('sharpe_ratio', 0):.2f}
Max Drawdown: {stats.get('max_drawdown', 0):.2f}%

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        await self._send_message(message)
    
    async def _send_message(self, text: str):
        """Send message to Telegram chat."""
        if not self.enabled or not self.api_url:
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "HTML"
                }
                async with session.post(self.api_url, json=data) as response:
                    if response.status != 200:
                        logger.warning(f"Telegram notification failed: {response.status}")
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")


if __name__ == "__main__":
    notifier = TelegramNotifier()
    print(f"Telegram Notifier initialized (enabled: {notifier.enabled})")
