from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from app.database.requests import get_all
from app.database.models import Litwork

yes_no = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Yse"), KeyboardButton(text="No")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
)

next_or_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Continue to study"), KeyboardButton(text="Menu")]
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
        [InlineKeyboardButton(text="Questionary", callback_data="questionary")],
        [InlineKeyboardButton(text="Discussion", callback_data="discussion")],
        [InlineKeyboardButton(text="Idea", callback_data="idea")],
        [InlineKeyboardButton(text="Menu", callback_data="menu")]
    ]
)

answer_options_basic = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3"), KeyboardButton(text="4")]
    ],
    resize_keyboard=True
)



async def litwork_builder():
    litworks = await get_all(Litwork)
    builder = InlineKeyboardBuilder()
    for litwork in litworks:
        builder.add(InlineKeyboardButton(text=litwork.title, callback_data=f"litwork_{litwork.id}"))
    return builder.adjust(2).as_markup()


async def answer_options_builder(answer_options: list[str]):
    builder = ReplyKeyboardBuilder()
    for answer_option in answer_options:
        builder.add(KeyboardButton(text=answer_option))
    return builder.adjust(2).as_markup()
