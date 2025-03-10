import uuid
import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy.exc import IntegrityError
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Filter, CommandStart, Command
from aiogram.fsm.context import FSMContext
from app.states.admin_states import Newsletter, RegOrganization
from app.database.requests.setters_and_getters import get_all_users, set_organization
import app.keyboards.keyboards as kb

load_dotenv()
admin = Router()

class Admin(Filter):
    def __init__(self):
        self.admins = [738490613]

    async def __call__(self, message: Message):
        return message.from_user.id in self.admins


@admin.message(Admin(), Command('admin'))
async def cmd_admin(message: Message):
    await message.answer(f'Добро пожаловать в бот, администратор {message.from_user.first_name}!')


@admin.message(Admin(), Command('newsletter'))
async def newsletters(message: Message, state: FSMContext):
    await state.set_state(Newsletter.message)
    await message.answer("Введите сообщение для рассылки")

@admin.message(Newsletter.message)
async def newsletter_message(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Рассылка началась')
    users = await get_all_users()
    for user in users:
        try:
            await message.send_copy(chat_id=user.tg_id)
        except Exception as e:
            print(e)
    await message.answer("Рассылка завершена")


@admin.message(Admin(), Command('add_organization'))
async def add_organization(message: Message, state: FSMContext):
    await state.set_state(RegOrganization.name)
    await message.answer("Введите полное название организации")
    
@admin.message(RegOrganization.name)
async def regorg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegOrganization.legal_address)
    await message.answer("Введите полный юридический адрес организации")

@admin.message(RegOrganization.legal_address)
async def regorg_ask_quotes(message: Message, state: FSMContext):
    await state.update_data(legal_address=message.text)
    org_data = await state.get_data()
    invite_code = str(uuid.uuid4())
    try:
        await set_organization(invite_code=invite_code, **org_data)
        await message.answer(f'Организация "{org_data['name']}" зарегистрирована\ninvite_code: {invite_code}')

    except IntegrityError:  # duplicated invite_code
        await message.answer(f'Компания с invite_code = {invite_code} уже существует')
    await state.clear()
