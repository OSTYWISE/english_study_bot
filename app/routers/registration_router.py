import datetime
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from app.database.requests.requests import update_student, get_student, \
    get_teacher, get_organization, update_org, update_teacher
from app.states.registraion_states import UserRegistraion
import app.keyboards.keyboards as kb


reg = Router()


@reg.message(CommandStart())
async def cmd_regstart(message: Message, state: FSMContext) -> None:
    await message.answer(
        f"Приветствую, {hbold(message.from_user.full_name)}!\n"
        "Я твой помощник в учебе с искусственным интеллектом (ИИ) внутри. Я помогу тебе изучить то, что ты захочешь. "
        "Вижу, что ты еще не зарегистрирован")
    await message.answer("Чтобы начать пользоваться ботом, нужно пройти короткую регистрацию, которая займет около 5 минут")
    await message.answer("Для этого в сообщении ниже введи пригласительный код (invite_code), который тебе выдала школа или администратор бота")
    await state.set_state(UserRegistraion.invite_code)


@reg.message(UserRegistraion.invite_code)
async def userreg_invite_code(message: Message, state: FSMContext):
    student = await get_student(message.text.strip(), registration_flg=True)
    teacher = await get_teacher(message.text.strip(), registration_flg=True)
    organization = await get_organization(message.text.strip(), registration_flg=True)
    if student is not None:
        user = student
        await state.update_data(user_type='student')
    elif teacher is not None:
        user = teacher
        await state.update_data(user_type='teacher')
    elif organization is not None:  # final step for Organization
        await update_org(tg_id=message.from_user.id, invite_code=message.text.strip())
        await message.answer("✅ Подзравляю с успешной регистрацией!\n")
        await message.answer("ЗДЕСЬ БУДЕТ ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ БОТА ДЛЯ ОРГАНИЗАЦИИ")  # todo()
        await state.clear()
        return
    else:
        await message.answer(
            "К сожалению, я не нашел твое приглашение. Возможно школа или администратор еще не успели добавить тебя в списки.\n"
            "Проверь, что ты скопировал пригласительный код верно и попробуй еще раз (/start) "
            "Если проблема не решается, ты можешь оставить обратную связь, используя "
            "команду /feedback, и мой администратор напишет тебе для решения проблемы")
        await state.clear()
        return

    if user.tg_id is not None:
        await message.answer(
            "Другой пользователь уже зарегистрировался с этим пригласительным кодом.\n"
            "Проверь, что код пренадлежит тебе. Попробуй пройти регистрация еще раз /start\n")
        await message.answer(
            "Если ты указал все верно, мой администратор поможет тебе.\n"
            "Расскажи о проблеме используя команду /feedback")
        await state.clear()
        return
    await state.update_data(invite_code=message.text.strip())
    await state.update_data(tg_id=message.from_user.id)
    await message.answer("Пожалуйста, поделись своим номером телефона", reply_markup=kb.share_phone_number)
    await state.set_state(UserRegistraion.phone)


@reg.message(UserRegistraion.phone)
async def userreg_phone(message: Message, state: FSMContext):
    if message.contact:
        phone_number = message.contact.phone_number
    else:
        phone_number = message.text

    await state.update_data(phone=phone_number)
    await message.answer("Введи дату рождения в формате ДД.ММ.ГГГГ, например 28.03.2008", reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserRegistraion.birth_date)


@reg.message(UserRegistraion.birth_date)
async def userreg_birth_date(message: Message, state: FSMContext):
    birth_date_text = message.text.strip()

    try:
        birth_date = datetime.datetime.strptime(birth_date_text, "%d.%m.%Y").date()
    except ValueError:
        await message.answer("❌ Введите дату в формате ДД.ММ.ГГГГ")
        return

    await state.update_data(birth_date=str(birth_date))
    user_data = await state.get_data()
    if user_data['user_type'] == 'teacher':  # final or prefinal stage for teacher
        # await state.set_state(UserRegistraion.personal_info)
        # await message.answer("Расскажи немного о себе (не больше 50 слов)")
        await update_teacher(
            tg_id=message.from_user.id, user_data=user_data, invite_code=user_data["invite_code"]
            )
        await message.answer("✅ Подзравляю с успешной регистрацией!\n")
        await message.answer("ЗДЕСЬ БУДЕТ ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ БОТА ДЛЯ УЧИТЕЛЕЙ")  # todo()
        return 

    else:  # user_data['user_type'] == 'student':
        await update_student(
            tg_id=user_data['tg_id'], user_data=user_data,
            invite_code=user_data['invite_code']
            )
        await message.answer("✅ Подзравляю с успешной регистрацией!\n")
        await message.answer("ЗДЕСЬ БУДЕТ ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ БОТА ИЛИ ВЫЗОВ КОМАНДЫ ХЕЛП")  # todo()
        await message.answer("Теперь давай настроим бота для комфортного пользования. Для этого нажимай /settings")
    await state.clear()
    return


@reg.message(UserRegistraion.personal_info)  # for teachers only
async def userreg_personal_info(message: Message, state: FSMContext):
    await state.update_data(personal_info=message.text)
    user_data = await state.get_data()
    await update_teacher(
        tg_id=message.from_user.id, user_data=user_data, invite_code=user_data["invite_code"]
        )
    await message.answer("✅ Подзравляю с успешной регистрацией!\n")
    await message.answer("ЗДЕСЬ БУДЕТ ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ БОТА ДЛЯ УЧИТЕЛЕЙ")  # todo()
    await state.clear()


@reg.message()
async def userreg_llm_regime(message: CallbackQuery):
    await message.answer(
        "К сожалению, только зарегистрированные пользователи имеют доступ к функционалу этого бота.\n"
        "Чтобы пройти регистрацию, нажимай /start, и я помогу тебе в этом непростом мире учебы")