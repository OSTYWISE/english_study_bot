import asyncio
import os
import aiohttp
# from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties

# Load environment variables
# load_dotenv()
TOGETHER_AI_API_KEY = os.environ.get("TOGETHER_AI_API_KEY")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()

# Define states for FSM
class LearningState(StatesGroup):
    choosing_topic = State()
    waiting_for_answer = State()

# Dictionary to store user tasks
user_tasks = {}

async def generate_task(topic: str) -> str:
    """Fetch a task from Together AI's DeepSeek model."""
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_AI_API_KEY}",
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

async def check_answer(task: str, user_answer: str) -> str:
    """Check if the user's answer is correct using Together AI."""
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_AI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
        "messages": [
            {"role": "user", "content": f"Given the task: {task}\nThe student answered: {user_answer}.\nEvaluate the correctness and explain the correct solution."}
        ],
        "max_tokens": 300
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            data = await response.json()
            answer = data.get("choices", [{}])[0].get("message", {}).get("content", "Failed to check the answer.")
            return 'Your request was executed'

@dp.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    """Starts the bot and asks the user to choose a learning topic."""
    await message.answer("Welcome! What topic would you like to learn? (e.g., differentiation, linear algebra, physics)")
    await state.set_state(LearningState.choosing_topic)

@dp.message(LearningState.choosing_topic)
async def choose_topic(message: Message, state: FSMContext):
    """Receives the user's chosen topic and generates a task."""
    topic = message.text.strip()
    task = await generate_task(topic)

    # Store task for this user
    user_tasks[message.from_user.id] = task

    await message.answer(f"Here's your task:\n\n<b>{task}</b>\n\nPlease provide your answer.")
    await state.set_state(LearningState.waiting_for_answer)

@dp.message(LearningState.waiting_for_answer)
async def receive_answer(message: Message, state: FSMContext):
    """Receives the user's answer and checks its correctness."""
    user_id = message.from_user.id
    user_answer = message.text.strip()

    # Get the stored task
    task = user_tasks.get(user_id, "No task found.")
    
    # Check answer using AI
    feedback = await check_answer(task, user_answer)

    await message.answer(f"<b>Feedback:</b>\n{feedback}")
    await state.clear()

@dp.message(Command("set_global_settings"))
async def set_global_settings(message: Message, state: FSMContext):
    """Allows the user to change the topic they want to learn."""
    await message.answer("Please enter a new topic you would like to learn:")
    await state.set_state(LearningState.choosing_topic)

async def main():
    """Start the bot."""
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
