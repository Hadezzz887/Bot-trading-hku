import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import *
from scanner import run_scanner

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

AUTO = True

@dp.message(Command("start"))
async def start(message: types.Message):

    await message.answer(
        "🚀 Pump.fun Smart Money Bot Online"
    )

@dp.message(Command("ping"))
async def ping(message: types.Message):

    await message.answer("pong")

@dp.message(Command("auto_on"))
async def auto_on(message: types.Message):

    global AUTO
    AUTO = True

    await message.answer("✅ AUTO ON")

@dp.message(Command("auto_off"))
async def auto_off(message: types.Message):

    global AUTO
    AUTO = False

    await message.answer("⛔ AUTO OFF")

async def main():

    await bot.send_message(
        chat_id=CHAT_ID,
        text="🚀 BOT STARTED"
    )

    asyncio.create_task(
        run_scanner(bot)
    )

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
