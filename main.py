import os
import warnings
import asyncio
import logging

from dotenv import load_dotenv
from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.user_router import user
from app.database.models import async_main
warnings.filterwarnings("ignore", category=UserWarning)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start working with bot"),
        BotCommand(command="help", description="Instructions for working with bot"),
        BotCommand(command="change_litwork", description="Change the literary work"),
        BotCommand(command="questionary", description="Test your knowledge"),
        BotCommand(command="discuss", description="Discuss the literary work"),
        BotCommand(command="idea", description="Generate new idea"),
        BotCommand(command="stop", description="Stop the discussion"),
    ]
    await bot.set_my_commands(commands)


async def main():
    """
    Main script for launching bot
    Args:
        config (DictConfig): hydra experiment config.
    """
    load_dotenv()
    # TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
    TG_BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    # together_client = TogetherAIClient(api_key=TOGETHER_API_KEY)
    bot = Bot(token=TG_BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_routers(user)
    await set_commands(bot)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    await dp.start_polling(bot)


async def startup(dispatcher: Dispatcher):
    await async_main()
    print('Starting up...')


async def shutdown(dispatcher: Dispatcher):
    print('Shutting down...')


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.DEBUG)
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
