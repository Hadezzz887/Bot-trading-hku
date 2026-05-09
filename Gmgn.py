import aiohttp

async def get_smart_money(token_address):

    url = f"https://gmgn.ai/defi/quotation/v1/tokens/sol/{token_address}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                data = await r.json()

                buys = data.get("data", {})

                smart_wallets = buys.get("smart_money_count", 0)
                volume = buys.get("smart_buy_volume", 0)

                return {
                    "wallets": smart_wallets,
                    "volume": volume
                }

    except:
        return {
            "wallets": 0,
            "volume": 0
        }
