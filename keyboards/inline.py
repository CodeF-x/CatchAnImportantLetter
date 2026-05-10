import os

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()


async def profile_keyboard():
    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text="📧 Изменить почту",
        callback_data="change_email")
    )

    builder.row(
        types.InlineKeyboardButton(
            text="🔐 Изменить пароль",
            callback_data="change_password")
    )

    builder.row(types.InlineKeyboardButton(
        text="📱 Изменить номер телефона",
        callback_data="change_phone")
    )

    builder.row(types.InlineKeyboardButton(
        text="🔄 Обновить данные",
        callback_data="refresh_profile")
    )

    return builder.as_markup()


async def password_instruction():
    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text="🔗 yandex",
        url=os.getenv("YANDEX_INSTRACTION"))
    )
    builder.row(types.InlineKeyboardButton(
        text="🔗 mail",
        url=os.getenv("MAIL_INSTRACTION"))
    )
    builder.row(types.InlineKeyboardButton(
        text="🔗 gmail",
        url=os.getenv("GOOGLE_INSTRACTION"))
    )
    builder.row(types.InlineKeyboardButton(
        text="🔗 icloud",
        url=os.getenv("APPLE_INSTRACTION"))
    )
    builder.row(types.InlineKeyboardButton(
        text="🔗 outlook",
        url=os.getenv("OUTLOOK_INSTRACTION"))
    )
    return builder.as_markup()


async def list_keyboard():
    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text="🗑 Удалить письмо из списка",
        callback_data="delete_message")
    )
    return builder.as_markup()


async def params_keyboard(save):
    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text="🔄 Обновить данные",
        callback_data="refresh_params")
    )
    if save:
        builder.row(types.InlineKeyboardButton(
            text="✅ Сохранять средние",
            callback_data="save_midle")
        )
    else:
        builder.row(types.InlineKeyboardButton(
            text="❌ Не сохранять средние",
            callback_data="save_midle")
        )
    builder.row(types.InlineKeyboardButton(
        text="📍 Изменить учитываемое",
        callback_data="include_params")
    )
    builder.row(types.InlineKeyboardButton(
        text="🗑 Изменить избегаемое",
        callback_data="exclude_params")
    )
    return builder.as_markup()


async def phone_del_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="❌ Использовать без номера",
        callback_data="close_number"
    ))
    return builder.as_markup()
