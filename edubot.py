import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.markdown import hbold
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.state import State
from aiogram.client.default import DefaultBotProperties

import re
import json
from bs4 import BeautifulSoup
import aiosqlite
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = "bot_history.db"
router = Router()

def todo():
    print("TO DO task")

async def init_db() -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS history (
            user_id INTEGER,
            query TEXT,
            query_id INTEGER,
            UNIQUE(query_id)
        )
        """)
        await db.commit()

class LearningState(StatesGroup):
    choosing_topic = State()
    waiting_for_answer = State()

@router.message(Command('start'))
async def start_handler(message: Message) -> None:
    await message.reply(
        f"Приветствую, {hbold(message.from_user.full_name)}! Я твой помошник с искутсвенным интеллектом (ИИ) внутри."
        "Я помогу тебе изучить то, что ты захочешь. Если ты зашел впервые, выполни /help и посмотри что я умею."
        "Если готов обучаться, нажимай /start_learning."
        )

@router.message(Command("settings"))
async def help_handler(message: Message):
    await message.answer(f"Здесь ты в будущем сможешь настроить параметры для взаимодействия со мной для идеального обучения")
    # todo()

@router.message(Command("help"))
async def start_handler(message: Message):
    await message.answer(f"Здесь ты очень скоро найдешь описание бота и всю мою функциональность")

@router.message()
async def message_handler(message: Message):
    await message.answer(f"Кажется ты хочешь начать учиться вместе со мной. Для этого ты можешь ввыести \"/\" и выбрать нужную опцию для себя")

async def main() -> None:
    await init_db()

    TG_BOT_TOKEN = os.getenv("BOT_TOKEN")

    if bot_token is None:
        bot_token = ''
    bot = Bot(token=TG_BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())