import os
from dotenv import load_dotenv
import datetime
import aiohttp
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from app.database.requests.setters_and_getters import set_student
from app.states.user_states import UserRegistraion

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
user = Router()


@user.message(CommandStart())
# Функция старта должна зависеть от того есть ли человек уже в базе (tg_id), 
# если нет - смотрим по invitation_code сначала по организациям, затем по преподавателям и затем по студентам.
# Если не нашли - ссори, если нашли - регистрация
async def cmd_start(message: Message, state: FSMContext) -> None:
    # if this is a student:

    # await set_student(message.from_user.id)
    await message.answer(
        f"Приветствую, {hbold(message.from_user.full_name)} with id {message.from_user.id}! Я твой помощник с искусственным интеллектом (ИИ) внутри. "
        "Я помогу тебе изучить то, что ты захочешь. Если ты зашел впервые, выполни /help и посмотри, что я умею. "
        "Если готов обучаться, нажимай /start_learning"
    )
    await message.answer("Чтобы начать пользоваться ботом нужно пройти короткую регистрацию.")
    await message.answer("Как к тебе обращаться в дальнейшем?")
    await state.set_state(UserRegistraion.name)


@user.message(UserRegistraion.name)
async def userreg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Поделиться номером телефона", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Пожалуйста, поделись своим номером телефона", reply_markup=keyboard)
    await state.set_state(UserRegistraion.phone)


@user.message(UserRegistraion.phone)
async def userreg_phone(message: Message, state: FSMContext):
    if message.contact:
        phone_number = message.contact.phone_number
    else:
        phone_number = message.text

    await state.update_data(phone=phone_number)
    await message.answer("Введи дату рождения.", reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserRegistraion.birth_date)


@user.message(UserRegistraion.birth_date)
async def userreg_birth_date(message: Message, state: FSMContext):
    birth_date_text = message.text.strip()

    try:
        # Try to parse date of birth
        birth_date = datetime.datetime.strptime(birth_date_text, "%d.%m.%Y").date()
    except ValueError:
        await message.answer("❌ Введите дату в формате ДД.ММ.ГГГГ. Например 28.03.2008")
        return

    await state.update_data(birth_date=str(birth_date))

    user_data = await state.get_data()
    # todo() - добавить запись в базу данных update_student()
    await message.answer(
        f"✅ Регистрация успешно завершена!\n\nИмя: {user_data['name']}"
        f"\nТелефон: {user_data['phone']}\nДата рождения: {user_data['birth_date']}")
    await state.clear()


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