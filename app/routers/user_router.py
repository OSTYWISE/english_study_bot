import os
from dotenv import load_dotenv
import datetime
import aiohttp
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import Filter, Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from app.database.requests.requests import set_student, update_student, \
    get_student, get_const_value, get_value_by_id, update_bot_settings
from app.database.models import Student, Topic, TaskType, Difficulty, PersRegime, \
    LLMRegime, Subject, Task
from app.states.user_states import BotSettings, StudyProcess
import app.keyboards.keyboards as kb
from app.llm.LLMClient import generate_task, generate_explanation, generate_thoery

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
user = Router()


class IsStudent(Filter):
    async def __call__(self, message: Message) -> bool:
        student = await get_student(message.from_user.id)
        return student is not None


# Start only for Students
@user.message(IsStudent(), CommandStart())
async def cmd_regstart(message: Message, state: FSMContext) -> None:
    await message.answer(
        f"Приветствую, {hbold(message.from_user.full_name)}!\n"
        "Я твой помощник в учебе с искусственным интеллектом (ИИ) внутри. Я помогу тебе изучить то, что ты захочешь. "
        "ЗДЕСЬ БУДЕТ ТЕКСТ О ТОМ КАК ПОЛЬЗОВАТЬСЯ БОТОМ")
    await message.answer("Если ты хочешь сменить настройки бота, используй команду /settings")


@user.message(IsStudent(), Command('settings'))
async def settings_handler(message: Message, state: FSMContext):
    await message.answer("НАСТРОЙКА ПАРАМЕТРОВ БОТА")  # todo()
    await state.set_state(BotSettings.pers_regime)
    await state.update_data(tg_id = message.from_user.id)
    await message.answer("Выбери персональный режим работы с ботом", reply_markup=await kb.pers_regim_builder())


@user.callback_query(BotSettings.pers_regime)
async def userreg_pers_regime(callback: CallbackQuery, state: FSMContext):
    await state.update_data(pers_regime_id=int(callback.data[len('pers_regime_'):]))
    await callback.answer("Персональный режим работы с ботом выбран")
    await callback.message.edit_text("Выбери тематику", reply_markup=await kb.topic_builder())
    await state.set_state(BotSettings.topic)


@user.callback_query(BotSettings.topic)
async def userreg_topic(callback: CallbackQuery, state: FSMContext):
    await state.update_data(topic_id=int(callback.data[len('topic_'):]))
    await callback.answer("Тематика выбрана")
    await callback.message.edit_text("Выбери уровень сложности", reply_markup=await kb.difficulty_builder())
    await state.set_state(BotSettings.difficulty)

@user.callback_query(BotSettings.difficulty)
async def userreg_difficulty(callback: CallbackQuery, state: FSMContext):
    await state.update_data(difficulty_id=int(callback.data[len('difficulty_'):]))
    await callback.answer("Сложность выбрана")
    await callback.message.edit_text("Выбери тип задач", reply_markup=await kb.task_type_builder())
    await state.set_state(BotSettings.task_type)

@user.callback_query(BotSettings.task_type)
async def userreg_task_type(callback: CallbackQuery, state: FSMContext):
    await state.update_data(task_type_id=int(callback.data[len('task_type_'):]))
    await callback.answer("Тип задачи выбран")
    await callback.message.edit_text("Выбери режим ответов бота", reply_markup=await kb.llm_regime_builder())
    await state.set_state(BotSettings.regime)


@user.callback_query(BotSettings.regime)
async def userreg_llm_regime(callback: CallbackQuery, state: FSMContext):
    await state.update_data(llm_regime_id=int(callback.data[len('llm_regime_'):]))
    await callback.answer("Режим ответов бота выбран")
    user_data = await state.get_data()
    await update_bot_settings(tg_id=user_data['tg_id'], user_data=user_data)
    await callback.message.edit_text("Ура!!! Настройки бота сохранены ✅")
    await callback.message.answer("Теперь давай начнем учиться /study")
    await state.clear()


@user.message(IsStudent(), Command('help'))
async def help_handler(message: Message):
    await message.answer("ЗДЕСЬ ТЫ НАЙДЕШЬ ОПИСАНИЕ БОТА И ВСЮ ЕГО ФУНКЦИОНАЛЬНОСТЬ, КОМАНДЫ")  # todo()


@user.message(IsStudent(), Command('feedback'))
async def settings_handler(message: Message):
    await message.answer("ЗДЕСЬ МОЖНО БУДЕТ СООБЩИТЬ О ПРОБЛЕМЕ")  # todo()


# Not a final function. Need to add user and to parse data from database about the user -> global data,
# if there is a local data - use it.
@user.message(IsStudent(), Command('study'))
async def study_handler(message: Message, state: FSMContext) -> None:
    # todo() Добавить логику сэмплинга из базы данных
    # todo() добавить keyboards_builders for some task_type, different function behavior for each task_type
    student = await get_student(message.from_user.id)
    if not student:
        await message.answer(
            "Этот функционал доступен только для зарегестрированных пользователей. "
            "Для регистрации попроси у своего учителя выдать тебе пригласительный код, "
            "после чего вводи команду /start и начинай пользоваться ботом")
        return
    pers_regime = await get_value_by_id(PersRegime, student.pers_regime_id)
    llm_regime = await get_value_by_id(LLMRegime, student.regime_id)
    topic = await get_value_by_id(Topic, student.topic_id)
    task_type = await get_value_by_id(TaskType, student.task_type_id)
    difficulty = await get_value_by_id(Difficulty, student.difficulty_id)

    await state.set_state(StudyProcess.ask_generate)
    await state.update_data(pers_regime=pers_regime, llm_regime=llm_regime,
                            topic=topic, task_type=task_type, difficulty=difficulty)
    await message.answer("Генерируем?", reply_markup=kb.generate_or_menu)


@user.message(F.text == "Сгенерировать задачу")
async def study_generate_task(message: Message, state: FSMContext):
    # todo() ChatAction - Генерация ...

    user_data = await state.get_data()
    await message.answer("Начинаю генерацию задачи...", reply_markup=ReplyKeyboardRemove())
    task, answer, explanation = await generate_task(user_data)
    await state.update_data(task=task, answer=answer, explanations=[explanation])

    await message.answer(task)
    if user_data['task_type'] == 'Да/Нет':
        await message.answer("Выбери свой ответ:", reply_markup=kb.yes_no)
    else:
        await message.answer("Напиши свой ответ:")
    await state.set_state(StudyProcess.answer)


@user.message(F.text == "В меню")
async def study_to_menu(message: Message, state: FSMContext):
    await message.answer('Для работы с мной нажми три полоски слева и выбери команду',
                         reply_markup=ReplyKeyboardRemove())
    await state.clear()


@user.message(StudyProcess.answer)
async def userreg_check_answer(message: Message, state: FSMContext):
    await state.update_data(student_answer=message.text)
    user_data = await state.get_data()
    if message.text == user_data['answer']:
        await message.answer("Правильно!", reply_markup=ReplyKeyboardRemove())
        await message.answer("Хочешь получить объяснение почему этот ответ правильный?", reply_markup=kb.yes_no)
        await state.set_state(StudyProcess.ask_explain)
    else:
        await message.answer("Ответ неверный! Ниже я распишу решение этой задачи", reply_markup=ReplyKeyboardRemove())
        await message.answer(f"Правильный ответ: {user_data['answer']}")
        await message.answer(user_data['explanations'][0])
        await message.answer("Что делаем дальше?", reply_markup=kb.whats_next)
        await state.set_state(StudyProcess.whats_next)


@user.message(StudyProcess.ask_explain)
async def userreg_give_explanation(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text == "Да":
        await message.answer(user_data['explanations'][0])

    await message.answer("Что делаем дальше?", reply_markup=kb.whats_next)
    await state.set_state(StudyProcess.whats_next)


@user.callback_query(StudyProcess.whats_next)
async def userreg_whats_next(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    if callback.data == 'menu':
        await callback.message.edit_text(
            'Для работы с мной нажми три полоски слева и выбери команду')
        await state.clear()
    elif callback.data == 'detailed_explain':
        await callback.message.edit_text("Генерирую объяснение...")
        new_explanation = await generate_explanation(user_data)
        await callback.message.answer(new_explanation)
        await state.update_data(explanations=user_data['explanations'] + [new_explanation])
        await callback.message.answer("Что делаем теперь?", reply_markup=kb.whats_next)
    elif callback.data == 'theory_explain':
        await callback.message.edit_text("Сейчас расскажу, как решать такие задачи.\nГенерирую...")
        new_theory = await generate_thoery(user_data)
        await callback.message.answer(new_theory)
        await state.update_data(theory=new_theory)
        await callback.message.answer("Что делаем теперь?", reply_markup=kb.whats_next)
    else:
        await callback.message.edit_text("Какую по сложности задачу сгенерировать?", reply_markup=kb.change_difficulty)
        await state.set_state(StudyProcess.next_task)


@user.callback_query(StudyProcess.next_task)
async def userreg_next_task(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await callback.message.edit_text(f"Хорошо, сделаю {callback.data}")
    await state.update_data(prev_task=user_data['task'], change_difficulty=callback.data)
    await study_generate_task(callback.message, state)



# @user.message(IsStudent(), Command('learn_topic'))
# async def learn_topic_handler(message: Message, state: FSMContext):
#     """Start topic learning with chatting regime to go in depth not only with solving problems,
#     but also with consuming infomration / theory on the topic. 

#     Args:
#         message (Message)
#     """
#     # todo()  Если и запускать, то здесь должен быть жесткий системный промпт,
#     # который ограничит выход за пределы обсуждаемой темы
#     await message.answer("ЗДЕСЬ БУДЕТ РЕЖИМ ЧАТИНГА С БОТОМ ПО ОПРЕДЕЛЕННОЙ ТЕМЕ")  # todo()




# Закомментил только на время теста, чтобы я мог админом все роутеры юзать
# @user.message(IsStudent())
# async def default_handler(message: Message):
#     await message.answer(
#         "Такой операции нет. Ты можешь ознакомиться с инструкцией по работе со мной, используя команду /help"
#         )
