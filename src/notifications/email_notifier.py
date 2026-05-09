#!/usr/bin/env python3
"""
Email notifications for trading events.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict
from src.utils.config import Config

logger = logging.getLogger(__name__)

class EmailNotifier:
    """Send email notifications for trading events."""
    
    def __init__(self, 
                 smtp_server: Optional[str] = None,
                 smtp_port: Optional[int] = None,
                 sender_email: Optional[str] = None,
                 sender_password: Optional[str] = None,
                 recipient_email: Optional[str] = None):
        self.smtp_server = smtp_server or Config.get('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or Config.get('EMAIL_SMTP_PORT', 587)
        self.sender_email = sender_email or Config.get('EMAIL_SENDER')
        self.sender_password = sender_password or Config.get('EMAIL_PASSWORD')
        self.recipient_email = recipient_email or Config.get('EMAIL_RECIPIENT')
        self.enabled = bool(self.sender_email and self.sender_password and self.recipient_email)
    
    def send_trade_signal(self, symbol: str, signal: float, confidence: float, 
                         sources: Dict[str, float]):
        """Send trade signal email notification."""
        if not self.enabled:
            return
        
        signal_type = "BUY" if signal > 0 else "SELL"
        
        subject = f"Trading Signal: {signal_type} {symbol}"
        body = f"""
        <html>
          <body>
            <h2>Trading Signal Alert</h2>
            <p><b>Signal Type:</b> {signal_type}</p>
            <p><b>Symbol:</b> {symbol}</p>
            <p><b>Signal Strength:</b> {signal:.2f}</p>
            <p><b>Confidence:</b> {confidence*100:.1f}%</p>
            
            <h3>Signal Sources:</h3>
            <ul>
              <li>Smart Money: {sources.get('smart_money', 0):.2f}</li>
              <li>News Sentiment: {sources.get('news', 0):.2f}</li>
              <li>Twitter Trend: {sources.get('twitter', 0):.2f}</li>
            </ul>
            
            <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
          </body>
        </html>
        """
        
        self._send_email(subject, body)
    
    def send_trade_execution(self, symbol: str, action: str, price: float, 
                            position_size: float):
        """Send trade execution email notification."""
        if not self.enabled:
            return
        
        subject = f"Trade Executed: {action.upper()} {symbol}"
        body = f"""
        <html>
          <body>
            <h2>Trade Execution Notification</h2>
            <p><b>Action:</b> {action.upper()}</p>
            <p><b>Symbol:</b> {symbol}</p>
            <p><b>Price:</b> ${price:.2f}</p>
            <p><b>Position Size:</b> {position_size:.2f}</p>
            
            <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
          </body>
        </html>
        """
        
        self._send_email(subject, body)
    
    def send_daily_report(self, stats: Dict):
        """Send daily performance report email."""
        if not self.enabled:
            return
        
        subject = "Daily Trading Performance Report"
        body = f"""
        <html>
          <body>
            <h2>Daily Performance Report</h2>
            <table border="1" cellpadding="10">
              <tr><td><b>Total Trades</b></td><td>{stats.get('total_trades', 0)}</td></tr>
              <tr><td><b>Winning Trades</b></td><td>{stats.get('winning_trades', 0)}</td></tr>
              <tr><td><b>Losing Trades</b></td><td>{stats.get('losing_trades', 0)}</td></tr>
              <tr><td><b>Win Rate</b></td><td>{stats.get('win_rate', 0):.1f}%</td></tr>
              <tr><td><b>Daily P&L</b></td><td>${stats.get('daily_pnl', 0):.2f}</td></tr>
              <tr><td><b>Sharpe Ratio</b></td><td>{stats.get('sharpe_ratio', 0):.2f}</td></tr>
              <tr><td><b>Max Drawdown</b></td><td>{stats.get('max_drawdown', 0):.2f}%</td></tr>
              <tr><td><b>Account Balance</b></td><td>${stats.get('balance', 0):.2f}</td></tr>
            </table>
            
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
          </body>
        </html>
        """
        
        self._send_email(subject, body)
    
    def _send_email(self, subject: str, body: str):
        """Send email using SMTP."""
        if not self.enabled:
            logger.warning("Email notifier not configured")
            return
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {self.recipient_email}")
        except Exception as e:
            logger.error(f"Error sending email: {e}")


if __name__ == "__main__":
    notifier = EmailNotifier()
    print(f"Email Notifier initialized (enabled: {notifier.enabled})")
