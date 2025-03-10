from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, CommandStart, Command
teacher = Router()

class Teacher(Filter):
    def __init__(self):
        self.teachers = [123, 456]

    async def __call__(self, message: Message):
        return message.from_user.id in self.teachers
    

@teacher.message(Teacher(), Command('teacher'))
async def cmd_start(message: Message):
    await message.answer('Добро пожаловать в бот, преподаватель!')