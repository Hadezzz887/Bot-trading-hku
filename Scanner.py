import aiohttp
import asyncio

from gmgn import get_smart_money
from twitter_scanner import get_x_score
from trader import buy_token
from config import *

POSITIONS = {}

async def fetch_tokens():

    url = "https://frontend-api.pump.fun/coins/latest"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                data = await r.json()
                return data

    except:
        return []

async def process_token(token, bot):

    try:

        name = token.get("name", "")
        address = token.get("mint")

        marketcap = token.get("usd_market_cap", 0)

        if marketcap < MIN_MC:
            return

        if marketcap > MAX_MC:
            return

        smart = await get_smart_money(address)

        x_score = await get_x_score(name)

        final_score = (
            smart["wallets"] * 20
        ) + x_score

        if smart["wallets"] < SMART_MONEY_MIN:
            return

        text = f"""
🚨 SMART MONEY DETECTED

TOKEN: {name}
MCAP: ${marketcap}
SMART WALLETS: {smart['wallets']}
X SCORE: {x_score}
FINAL SCORE: {final_score}

https://pump.fun/{address}
"""

        await bot.send_message(
            chat_id=CHAT_ID,
            text=text
        )

        if final_score >= 120:

            success = await buy_token(
                address,
                BUY_AMOUNT_SOL
            )

            if success:

                POSITIONS[address] = {
                    "name": name,
                    "entry": marketcap
                }

                await bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"✅ AUTO BUY {name}"
                )

    except Exception as e:
        print(e)

async def run_scanner(bot):

    scanned = set()

    while True:

        try:

            tokens = await fetch_tokens()

            for token in tokens:

                address = token.get("mint")

                if address in scanned:
                    continue

                scanned.add(address)

                asyncio.create_task(
                    process_token(token, bot)
                )

        except Exception as e:
            print(e)

        await asyncio.sleep(8)
