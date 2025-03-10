from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, CommandStart, Command

organization = Router()


class Organization(Filter):
    def __init__(self):
        self.organizations = [123, 456]

    async def __call__(self, message: Message):
        return message.from_user.id in self.organizations
    

@organization.message(Organization(), CommandStart())
async def cmd_start(message: Message):
    await message.answer('Добро пожаловать в бот, образовательная организация!')


