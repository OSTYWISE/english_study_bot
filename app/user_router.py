import os
import uuid
import random
import asyncio
from dotenv import load_dotenv
from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import Filter, Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from app.database.requests import get_student, get_litwork_by_id, set_or_update_student, get_litwork_by_name
from app.llm.LLMClient import generate_questionary, generate_idea, discuss_litwork
from app.user_states import UserSettings, Discussion, Idea, Questionary
from app.utils import question_to_text, has_litwork
import app.keyboards as kb
load_dotenv()


user = Router()


@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await message.answer(
        f"Hi, {hbold(message.from_user.full_name)}!\n"
        "I am your helper in \"Fantastic in World Literature\" course studying")
    help_message = "I have different options to organize your learning process:\n" + \
        "1. Generate questionary with 5 multiple choice questions about the literary work you'll choose (/questionary);\n" + \
        "2. Discussion mode: I'll be your classmate to discuss the plot and the meaning of engrossing scences(/discuss);\n" + \
        "3. Create a new non-obvious thought or idea on the certain topic in context of the text (/idea);\n"
    await message.answer(help_message)
    await message.answer("To start using the bot, you need to set the literary work you want to deep dive into.", reply_markup=await kb.litwork_builder())
    await state.set_state(UserSettings.litwork_choice)


@user.message(Command('change_litwork'))
async def settings_handler(message: Message, state: FSMContext):
    await message.answer("What literary work do you want to deep dive into now?", reply_markup=await kb.litwork_builder())
    await state.set_state(UserSettings.litwork_choice)


@user.callback_query(UserSettings.litwork_choice)
async def user_litwork_choice(callback: CallbackQuery, state: FSMContext):
    litwork = await get_litwork_by_id(int(callback.data.split('_')[1]))
    if litwork:
        await set_or_update_student(callback.from_user.id, litwork.id)
        await callback.message.answer("Your choice is saved! Now you can start studying.")
    else:
        await callback.message.answer("I don't know this work. Please, choose option from the list below.", reply_markup=await kb.litwork_builder())
    await state.clear()


@user.message(Command('help'))
async def help_handler(message: Message):
    help_message = "I am your helper in \"Drama and Theatre\" course studying\n\n" + \
        "I have different options to organize your learning process:\n" + \
        "1. Generate questionary with 5 multiple choice questions about the literary work you'll choose (/questionary);\n" + \
        "2. Discussion mode: I'll be your classmate to discuss the plot and the meaning of engrossing scences(/discuss);\n" + \
        "3. Create a new non-obvious thought or idea on the certain topic in context of the text (/idea);\n\n" + \
        "If you want to change your choice of text to analyze, use /change_litwork command."
    await message.answer(help_message)


@user.message(Command('questionary'))
async def questionary_handler(message: Message, state: FSMContext):
    has_litwork_flg = await has_litwork(message.from_user.id)
    if not has_litwork_flg:
        await message.answer("You need to choose a literary work first. Use /change_litwork command.")
        return
    student = await get_student(message.from_user.id)
    litwork = await get_litwork_by_id(student.litwork_id)

    with open(litwork.path, "r", encoding="utf-8") as file:
        litwork_text = file.read()

    await message.answer("Generating questionary...")
    await message.bot.send_chat_action(message.from_user.id, ChatAction.TYPING)

    questionary = await generate_questionary(litwork_text)
    await state.update_data(questionary=questionary)
    for question in questionary:
        if len(question['options']) != 4:
            await message.answer("Something went wrong. Please, try one more time /questionary")
            return

    await message.answer(
        "Question 1:\n" + question_to_text(questionary[0]), reply_markup=kb.answer_options_basic
        )  # 4 options
    await state.update_data(current_question_num=0, student_score=0)
    await state.set_state(Questionary.question)


@user.message(Questionary.question)
async def study_answer(message: Message, state: FSMContext):
    user_data = await state.get_data()
    current_question_num = user_data['current_question_num']

    if message.text.strip() == str(user_data['questionary'][current_question_num]['correct_answer']):
        await message.answer("Correct!", reply_markup=ReplyKeyboardRemove())
        user_data['student_score'] += 1
        await state.update_data(student_score=user_data['student_score'])
    else:
        await message.answer("Incorrect!", reply_markup=ReplyKeyboardRemove())
        await message.answer(f"Here is the correct answer: {user_data['questionary'][current_question_num]['correct_answer']}")

    if current_question_num < len(user_data['questionary']) - 1:
        current_question_num += 1
        await state.update_data(current_question_num=current_question_num)
        await message.answer(
            "Question " + str(current_question_num + 1) + ":\n" + \
            question_to_text(user_data['questionary'][current_question_num]), reply_markup=kb.answer_options_basic
            )
    else:
        await message.answer(f"You have finished the questionary with score {user_data['student_score']}/{len(user_data['questionary'])}!")
        await state.clear()




@user.message(Command('discuss'))
async def discuss_handler(message: Message, state: FSMContext):
    has_litwork_flg = await has_litwork(message.from_user.id)
    if not has_litwork_flg:
        await message.answer("You need to choose a literary work first. Use /change_litwork command.")
        return

    await message.answer("Let's start discussion. If you want to stop, just type /stop")
    await message.answer(f"Hi, {hbold(message.from_user.full_name)}! What do you want to discuss with me?")
    await state.update_data(discussion_messages=[
        {"role": "assistant", "text": f"Hi, {hbold(message.from_user.full_name)}! What do you want to discuss with me?"},
    ])
    await state.set_state(Discussion.discussion)


@user.message(Discussion.discussion)
async def study_discussion(message: Message, state: FSMContext):
    user_data = await state.get_data()
    student = await get_student(message.from_user.id)
    litwork = await get_litwork_by_id(student.litwork_id)
    with open(litwork.path, "r", encoding="utf-8") as file:
        litwork_text = file.read()

    user_data['discussion_messages'].append({"role": "user", "text": message.text})
    await state.update_data(discussion_messages=user_data['discussion_messages'])
    await message.bot.send_chat_action(message.from_user.id, ChatAction.TYPING)
    next_message = await discuss_litwork(user_data['discussion_messages'], litwork_text)
    await message.answer(next_message)
    user_data['discussion_messages'].append({"role": "assistant", "text": next_message})
    await state.update_data(discussion_messages=user_data['discussion_messages'])
    await state.set_state(Discussion.discussion)


@user.message(Command('stop'))
async def stop_discussion(message: Message, state: FSMContext):
    await message.answer("Discussion stopped.")
    await state.clear()


@user.message(Command('idea'))
async def idea_handler(message: Message, state: FSMContext):
    has_litwork_flg = await has_litwork(message.from_user.id)
    if not has_litwork_flg:
        await message.answer("You need to choose a literary work first. Use /change_litwork command.")
        return
    await message.answer("What topic do you need ideas on?")
    await state.set_state(Idea.wait_topic)


@user.message(Idea.wait_topic)
async def study_idea(message: Message, state: FSMContext):
    student = await get_student(message.from_user.id)
    litwork = await get_litwork_by_id(student.litwork_id)
    with open(litwork.path, "r", encoding="utf-8") as file:
        litwork_text = file.read()

    idea_text = await generate_idea(topic=message.text, litwork_text=litwork_text)
    await message.answer(idea_text)
    await state.clear()


@user.message()
async def default_handler(message: Message):
    await message.answer(
        "I have no such command. Use /help to see available commands"
        )
