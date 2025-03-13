from aiogram.fsm.state import State, StatesGroup


class TeacherRegistraion(StatesGroup):
    phone = State()
    birth_date = State()