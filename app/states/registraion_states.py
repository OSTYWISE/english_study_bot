from aiogram.fsm.state import State, StatesGroup


class UserRegistraion(StatesGroup):
    invite_code = State()
    phone = State()
    birth_date = State()
    personal_info = State()