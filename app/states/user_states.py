from aiogram.fsm.state import State, StatesGroup


class UserRegistraion(StatesGroup):
    name = State()
    phone = State()
    birth_date = State()
    # pers_regime = State()
    # difficulty = State()
    # task_type = State()
    # regime = State()


class Chat(StatesGroup):
    text = State()
    wait = State()