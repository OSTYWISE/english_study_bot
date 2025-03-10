from aiogram.fsm.state import State, StatesGroup

class Newsletter(StatesGroup):
    message = State()


class RegOrganization(StatesGroup):
    name = State()
    legal_address = State()