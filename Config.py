import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

BUY_AMOUNT_SOL = float(os.getenv("BUY_AMOUNT_SOL", 0.05))

MIN_MC = int(os.getenv("MIN_MC", 10000))
MAX_MC = int(os.getenv("MAX_MC", 25000))

SMART_MONEY_MIN = 2
MAX_DEV_HOLD = 15
X_TREND_THRESHOLD = 60
STOP_LOSS = -20
TAKE_PROFIT = 100

VIRAL_KEYWORDS = [
    "ai",
    "pepe",
    "cat",
    "dog",
    "ghibli",
    "anime",
    "elon",
    "trump",
    "meme",
    "pump",
    "sol",
]
