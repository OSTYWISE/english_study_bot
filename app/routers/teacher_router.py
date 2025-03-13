import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from aiogram.filters import Filter, CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from app.states.teacher_states import TeacherRegistraion
import app.keyboards.keyboards as kb
from app.database.requests.requests import get_value_by_id, get_teacher
from app.database.models import Teacher

teacher = Router()

class IsTeacher(Filter):
    async def __call__(self, message: Message) -> bool:
        teacher = await get_teacher(message.from_user.id)
        return teacher is not None


@teacher.message(IsTeacher(), CommandStart())
async def cmd_teacher(message: Message):
    await message.answer(f'Добро пожаловать в бот, преподаватель {message.from_user.first_name}!')


@teacher.message(IsTeacher(), Command('teacher'))
async def cmd_teacher(message: Message):
    await message.answer(f'Добро пожаловать в бот, преподаватель {message.from_user.first_name}!')


@teacher.message(IsTeacher(), Command('start_as_teacher'))
async def cmd_start_as_teacher(message: Message, state: FSMContext) -> None:
    # if this is a student:

    # await set_student(message.from_user.id)
    await message.answer(f'Добро пожаловать в бот, преподаватель {message.from_user.first_name}!')
    await message.answer("Чтобы начать пользоваться ботом нужно пройти короткую регистрацию для преподавателя.")
    await message.answer("Пожалуйста, поделитесь своим номером телефона", reply_markup=kb.share_phone_number)
    await state.set_state(TeacherRegistraion.phone)


@teacher.message(TeacherRegistraion.phone)
async def userreg_phone(message: Message, state: FSMContext):
    if message.contact:
        phone_number = message.contact.phone_number
    else:
        phone_number = message.text

    await state.update_data(phone=phone_number)
    await message.answer("Введите дату рождения.", reply_markup=ReplyKeyboardRemove())
    await state.set_state(TeacherRegistraion.birth_date)


@teacher.message(TeacherRegistraion.birth_date)
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
    # todo() - добавить запись в базу данных update_Isteacher()
    await message.answer(
        f"✅ Регистрация успешно завершена!\n\n"
        f"Телефон: {user_data['phone']}\nДата рождения: {user_data['birth_date']}")
    await state.clear()


# Закомментил только на время теста, чтобы я мог админом все роутеры юзать
# @teacher.message(IsTeacher())
# async def default_handler(message: Message):
#     await message.answer(
#         "Такой операции нет. Ты можешь ознакомиться с инструкцией по работе со мной, используя команду /help"
#         )