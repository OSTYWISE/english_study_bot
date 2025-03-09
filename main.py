import os
import hydra
import warnings
import asyncio
import logging

from dotenv import load_dotenv
from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
# from yandex_cloud_ml_sdk.auth import APIKeyAuth
# from hydra.utils import instantiate
# from omegaconf import DictConfig, OmegaConf

# from app.llm.LLMClient import TogetherAIClient
# from app.llm.prompter import Prompter
from app.routers import user, admin, teacher, organization
from app.database.models import async_main, drop_all_tables
warnings.filterwarnings("ignore", category=UserWarning)


async def main(config):
    """
    Main script for launching bot
    Args:
        config (DictConfig): hydra experiment config.
    """
    load_dotenv()
    # TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
    TG_BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    # together_client = TogetherAIClient(api_key=TOGETHER_API_KEY)
    # model_name = config.model.model_name
    # prompter = Prompter()
    bot = Bot(token=TG_BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()
    dp.include_routers(user, admin, teacher, organization)
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
        logging.basicConfig(level=logging.INFO)
        with hydra.initialize(version_base=None, config_path="app/configs"):
            config = hydra.compose(config_name="baseline")
        asyncio.run(main(config))
    except KeyboardInterrupt:
        pass
