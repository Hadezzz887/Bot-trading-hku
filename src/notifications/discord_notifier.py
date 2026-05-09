#!/usr/bin/env python3
"""
Discord notifications for trading events.
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Optional, Dict
from src.utils.config import Config

logger = logging.getLogger(__name__)

class DiscordNotifier:
    """Send Discord notifications for trading events."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or Config.get('DISCORD_WEBHOOK_URL')
        self.enabled = bool(self.webhook_url)
    
    async def send_trade_signal(self, symbol: str, signal: float, confidence: float, 
                               sources: Dict[str, float]):
        """Send trade signal notification to Discord."""
        if not self.enabled:
            return
        
        color = 3066993 if signal > 0 else 15158332  # Green for buy, red for sell
        signal_type = "🟢 BUY" if signal > 0 else "🔴 SELL"
        
        embed = {
            "title": f"{signal_type} Signal - {symbol}",
            "color": color,
            "fields": [
                {"name": "Signal Strength", "value": f"{signal:.2f}", "inline": True},
                {"name": "Confidence", "value": f"{confidence*100:.1f}%", "inline": True},
                {"name": "Smart Money", "value": f"{sources.get('smart_money', 0):.2f}", "inline": True},
                {"name": "News Sentiment", "value": f"{sources.get('news', 0):.2f}", "inline": True},
                {"name": "Twitter Trend", "value": f"{sources.get('twitter', 0):.2f}", "inline": True},
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Polymarket Trading Bot"}
        }
        
        await self._send_embed(embed)
    
    async def send_trade_execution(self, symbol: str, action: str, price: float, 
                                  position_size: float):
        """Send trade execution notification."""
        if not self.enabled:
            return
        
        color = 3066993 if action.upper() == "BUY" else 15158332
        
        embed = {
            "title": f"Trade Executed - {action.upper()}",
            "color": color,
            "fields": [
                {"name": "Symbol", "value": symbol, "inline": True},
                {"name": "Price", "value": f"${price:.2f}", "inline": True},
                {"name": "Position Size", "value": f"{position_size:.2f}", "inline": True},
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Polymarket Trading Bot"}
        }
        
        await self._send_embed(embed)
    
    async def send_profit_loss(self, pnl: float, return_pct: float):
        """Send P&L notification."""
        if not self.enabled:
            return
        
        color = 3066993 if pnl > 0 else 15158332
        emoji = "📈" if pnl > 0 else "📉"
        
        embed = {
            "title": f"{emoji} Trade Closed - P&L",
            "color": color,
            "fields": [
                {"name": "Profit/Loss", "value": f"${pnl:.2f}", "inline": True},
                {"name": "Return", "value": f"{return_pct:.2f}%", "inline": True},
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Polymarket Trading Bot"}
        }
        
        await self._send_embed(embed)
    
    async def send_error_alert(self, error_type: str, error_message: str):
        """Send error/alert notification."""
        if not self.enabled:
            return
        
        embed = {
            "title": f"⚠️ Alert - {error_type}",
            "color": 15158332,  # Red
            "fields": [
                {"name": "Error", "value": error_message, "inline": False},
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Polymarket Trading Bot"}
        }
        
        await self._send_embed(embed)
    
    async def send_daily_report(self, stats: Dict):
        """Send daily performance report."""
        if not self.enabled:
            return
        
        embed = {
            "title": "📊 Daily Performance Report",
            "color": 3066993,
            "fields": [
                {"name": "Trades", "value": f"{stats.get('total_trades', 0)}", "inline": True},
                {"name": "Win Rate", "value": f"{stats.get('win_rate', 0):.1f}%", "inline": True},
                {"name": "Daily P&L", "value": f"${stats.get('daily_pnl', 0):.2f}", "inline": True},
                {"name": "Balance", "value": f"${stats.get('balance', 0):.2f}", "inline": True},
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Polymarket Trading Bot"}
        }
        
        await self._send_embed(embed)
    
    async def _send_embed(self, embed: Dict):
        """Send embed to Discord webhook."""
        if not self.webhook_url:
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                data = {"embeds": [embed]}
                async with session.post(self.webhook_url, json=data) as response:
                    if response.status != 204:
                        logger.warning(f"Discord notification failed: {response.status}")
        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")


if __name__ == "__main__":
    notifier = DiscordNotifier()
    print(f"Discord Notifier initialized (enabled: {notifier.enabled})")
