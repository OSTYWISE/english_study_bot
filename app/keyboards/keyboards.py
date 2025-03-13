from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from app.database.models import Topic, PersRegime, LLMRegime, Subject, TaskType, Difficulty
from app.database.requests.requests import get_all

yes_no = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
)

share_phone_number = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Поделиться номером телефона", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

generate_or_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сгенерировать задачу"), KeyboardButton(text="В меню")]
    ],
    resize_keyboard=True
)

back = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back")]
    ]
)

whats_next = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Следующее задание", callback_data="next_task")],
        [InlineKeyboardButton(text="Объясни более подробно", callback_data="detailed_explain")],
        [InlineKeyboardButton(text="Расскажи как решать подобные задачи", callback_data="theory_explain")],
        [InlineKeyboardButton(text="В меню", callback_data="menu")]
    ]
)

change_difficulty = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Проще", callback_data="easier")],
        [InlineKeyboardButton(text="Такую же", callback_data="same")],
        [InlineKeyboardButton(text="Сложнее", callback_data="harder")],
    ]
)

async def topic_builder():
    topics = await get_all(Topic)
    builder = InlineKeyboardBuilder()
    # builder.add(InlineKeyboardButton(text="Выбрать текущую тематику", callback_data=current_topic_id))
    for topic in topics:
        builder.add(InlineKeyboardButton(text=topic.name, callback_data=f"topic_{topic.id}"))
    return builder.adjust(3).as_markup()


async def pers_regim_builder():
    pers_regimes = await get_all(PersRegime)
    builder = InlineKeyboardBuilder()
    for pers_regime in pers_regimes:
        builder.add(InlineKeyboardButton(text=pers_regime.name, callback_data=f"pers_regime_{pers_regime.id}"))
    return builder.adjust(3).as_markup()

async def difficulty_builder():
    difficulties = await get_all(Difficulty)
    builder = InlineKeyboardBuilder()
    for difficulty in difficulties:
        builder.add(InlineKeyboardButton(text=difficulty.name, callback_data=f"difficulty_{difficulty.id}"))
    return builder.adjust(1).as_markup()


async def task_type_builder():
    task_types = await get_all(TaskType)
    builder = InlineKeyboardBuilder()
    for task_type in task_types:
        builder.add(InlineKeyboardButton(text=task_type.name, callback_data=f"task_type_{task_type.id}"))
    return builder.adjust(2).as_markup()


async def llm_regime_builder():
    llm_regimes = await get_all(LLMRegime)
    builder = InlineKeyboardBuilder()
    for llm_regime in llm_regimes:
        builder.add(InlineKeyboardButton(text=llm_regime.name, callback_data=f"llm_regime_{llm_regime.id}"))
    return builder.adjust(2).as_markup()
