from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, CommandStart, Command
from app.database.models import Organization
from app.database.requests.requests import get_organization

organization = Router()


class IsOrganization(Filter):
    async def __call__(self, message: Message) -> bool:
        organization = await get_organization(message.from_user.id)
        return organization is not None
    

@organization.message(IsOrganization(), CommandStart())
async def cmd_start(message: Message):
    await message.answer(f'Добро пожаловать в бот, {message.from_user.full_name}!')


# Закомментил только на время теста, чтобы я мог админом все роутеры юзать
# @organization.message(IsOrganization())
# async def default_handler(message: Message):
#     await message.answer(
#         "Такой операции нет. Ты можешь ознакомиться с инструкцией по работе со мной, используя команду /help"
#         )