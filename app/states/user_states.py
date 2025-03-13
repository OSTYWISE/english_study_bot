from aiogram.fsm.state import State, StatesGroup


class BotSettings(StatesGroup):
    pers_regime = State()
    topic = State()
    difficulty = State()
    task_type = State()
    regime = State()


class StudyProcess(StatesGroup):
    ask_generate = State()
    generate = State()
    ask_answer = State()
    answer = State()
    ask_explain = State()
    whats_next = State()
    next_task = State()
