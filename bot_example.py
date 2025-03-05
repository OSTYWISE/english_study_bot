import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.markdown import hbold
from aiogram.client.session.aiohttp import AiohttpSession
import os

TOKEN = os.environ.get("BOT_TOKEN")

async def main():
    session = AiohttpSession()  # Optional session for performance optimization
    bot = Bot(token=TOKEN, session=session)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start_handler(message: Message):
        await message.answer(f"Hello, {hbold(message.from_user.full_name)}! Welcome to the bot.")

    @dp.message()
    async def echo(message: Message):
        await message.answer(f"You said: {message.text}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())