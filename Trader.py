import base58
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from config import RPC_URL, PRIVATE_KEY

client = Client(RPC_URL)

keypair = Keypair.from_bytes(
    base58.b58decode(PRIVATE_KEY)
)

async def buy_token(token_address, amount_sol):

    print(f"BUY {token_address} {amount_sol} SOL")

    # Integrasikan Jupiter Swap API di sini
    # https://station.jup.ag/docs/apis/swap-api

    return True

async def sell_token(token_address):

    print(f"SELL {token_address}")

    return True
