from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Список важных писем"), KeyboardButton(text="👤️ Профиль")],
        [KeyboardButton(text="⚙️ Параметры"), KeyboardButton(text="🔄️ Проверить сейчас")],
    ],
    resize_keyboard=True
)


async def phone_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(
        text="📱 Отправить номер",
        request_contact=True
    ))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


