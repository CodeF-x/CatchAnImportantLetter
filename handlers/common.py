import logging

from aiogram import Router, types, F
from aiogram.filters import Command
import os
from dotenv import load_dotenv
from keyboards.reply import main_menu
from database.repository import get_user_from_db, set_user, set_last_saved, del_user, set_politics_consent
from keyboards.inline import profile_keyboard
from services.mail import Mail
from services.ai import AI

router = Router()
load_dotenv()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    logo_id = os.getenv("LOGO_ID")
    await message.answer_photo(
        photo=logo_id,
        caption="Добро пожаловать!\n Этот бот поможет вам не пропустить важные и срочные письма."
    )
    user = await get_user_from_db(message.from_user.id)
    if user == None:
        await confirm_message(message)


async def confirm_message(message: types.Message):
    await message.answer(
        text=('Чтобы проолжить взаимодействие с ботом, необхожимо принять политику обработки персональных данных 📋\n\n'
              f'Отправляя команду /confirm, вы подтверждаете, что ознакомились и согласны с <a'
              f' href="{os.getenv("POLITICS")}">Политикой обработки персональных данных</a> 🔏'),
        parse_mode="HTML",
        disable_web_page_preview=True
    )


@router.message(Command("confirm"))
async def confirm(message: types.Message):
    await set_user(message.from_user.id)
    await set_politics_consent(message.from_user.id, "GRANTED", "2026/v1")
    await message.answer(
        text=(
            "Добро пожаловать! 🎉\n\nТеперь вам домтупен функционал бота.\nЧтобы удалить свой аккаунт и персональные данные"
            ", а также отказаться от согласия с политикой обработки персональных данных отправьте /delete_account 🗑️"),
        reply_markup=main_menu
    )


@router.message(Command("delete_account"))
async def delete_account(message: types.Message):
    await del_user(message.from_user.id)
    await set_politics_consent(message.from_user.id, "REVOKED", "2026/v1")
    await message.answer(
        text=(
            "Аккаунт и персональные данные успешно удалены, согласие с Политикой обработки персональных данных отозвано"),
        reply_markup=None
    )


@router.message(F.text == "👤️ Профиль")
async def show_profile(message: types.Message):
    user = await get_user_from_db(message.from_user.id)
    if user == None:
        await confirm_message(message)
        return
    answer = "Настройки:\n\n"
    answer += "<b>почта:</b> <u>" + (
        str(user.email_adress) if (user.email_adress != None) else "не задана") + "</u>\n"
    answer += "<b>пароль:</b> <u>" + ("скрыт" if (user.email_password != None) else "не задан") + "</u>\n"
    answer += "<b>телефон:</b> <u>" + (
        str(user.phone_number) if (user.phone_number != None) else "не задан") + "</u>\n"
    kb = await profile_keyboard()
    await message.answer(answer,
                         parse_mode="HTML",
                         reply_markup=kb)


@router.message(F.text == "🔄️ Проверить сейчас")
async def check_now(message: types.Message):
    user = await get_user_from_db(message.from_user.id)
    if user == None:
        await confirm_message(message)
        return
    if user.email_adress == None or user.email_password == None:
        await message.answer("Почта или пароль не заполнены ❌")
        return
    host = Mail.get_imap_host(user.email_adress)
    emails, last_checked = await Mail.fetch_latest_unread(host, user.email_adress, user.email_password, user.last_saved)
    any_changes = False
    await message.answer("Письма загружены, идет проверка 📝")
    for i in range(0, len(emails), 5):
        emails_cut = emails[i:i + 5]
        try:
            ai_answer = await AI.send_to_ai(emails_cut, user.include_prompt, user.exclude_prompt)
            logger.info(ai_answer)
            text, empty, for_sms = await AI.save_ai_result(ai_answer, user.telegram_id, save_midle=user.last_saved, )
            if last_checked != -1:
                await set_last_saved(user.telegram_id, last_checked)
            if not (empty):
                any_changes = True
                await message.answer(text, parse_mode="HTML")
        except Exception as e:
            logging.getLogger(__name__).error(f"Ошибка при работе с ии: {e}")
            await message.answer("Произошла ошибка ❌")
    if any_changes:
        await message.answer("Все сообщения проверены ✅")
    else:
        await message.answer("Ничего интересного не найдено ❌")
