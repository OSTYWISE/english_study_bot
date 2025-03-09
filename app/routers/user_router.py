import os
from dotenv import load_dotenv
import aiohttp
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.utils.markdown import hbold
from app.database.requests import set_student

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
user = Router()


@user.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await set_student(message.from_user.id)
    await message.answer(
        f"Приветствую, {hbold(message.from_user.full_name)}! Я твой помощник с искусственным интеллектом (ИИ) внутри. "
        "Я помогу тебе изучить то, что ты захочешь. Если ты зашел впервые, выполни /help и посмотри, что я умею. "
        "Если готов обучаться, нажимай /start_learning"
    )


@user.message(Command('settings'))
async def settings_handler(message: Message):
    await message.answer("Здесь ты в будущем сможешь настроить параметры для взаимодействия со мной для идеального обучения")


@user.message(Command('help'))
async def help_handler(message: Message):
    await message.answer("Здесь ты очень скоро найдешь описание бота и всю мою функциональность")


# Not a final function. Need to add user and to parse data from database about the user -> global data,
# if there is a local data - use it.
@user.message(Command('generate_task'))
async def generate_task(topic: str) -> str:
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
        }
    payload = {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
        "messages": [{"role": "user", "content": f"Generate a challenging {topic} task for a student."}],
        "max_tokens": 200
        }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            data = await response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "Failed to generate a task.")


@user.message()
async def default_handler(message: Message):
    await message.answer(
        "Такой операции нет. Наверное, ты хочешь начать учиться вместе со мной. " 
        "Для этого вводи /start и выбирай нужную тебе опцию")