from aiogram.fsm.state import State, StatesGroup


class UserSettings(StatesGroup):
    litwork_choice = State()


class Questionary(StatesGroup):
    question = State()
    wait_answer = State()


class Discussion(StatesGroup):
    discussion = State()

class Idea(StatesGroup):
    wait_topic = State()
