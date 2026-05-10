from aiogram import Router, types, F
from aiogram.filters import Command
import os
from dotenv import load_dotenv
from keyboards.reply import main_menu
from database.repository import get_user_from_db, set_user, set_last_saved
from keyboards.inline import profile_keyboard
from services.mail import Mail
from services.ai import AI

router = Router()
load_dotenv()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    logo_id = os.getenv("LOGO_ID")
    user = await get_user_from_db(message.from_user.id)
    if user == None:
        await set_user(message.from_user.id)
    await message.answer_photo(
        photo=logo_id,
        caption="Добро пожаловать!\n Этот бот поможет вам не пропустить важные и срочные письма.",
        reply_markup=main_menu
    )


@router.message(F.text == "👤️ Профиль")
async def show_profile(message: types.Message):
    user = await get_user_from_db(message.from_user.id)
    if user == None:
        await set_user(message.from_user.id)
        user = await get_user_from_db(message.from_user.id)
    answer = "Настройки:\n\n"
    answer += "<b>почта:</b> <u>" + (
        str(user.email_adress) if (user.email_adress != None) else "не задана") + "</u>\n"
    answer += "<b>пароль:</b> <u>" + ("скрыт" if (user.email_adress != None) else "не задан") + "</u>\n"
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
        await set_user(message.from_user.id)
        user = await get_user_from_db(message.from_user.id)
    host = Mail.get_imap_host(user.email_adress)
    emails, last_checked = await Mail.fetch_latest_unread(host, user.email_adress, user.email_password, user.last_saved)
    any_changes = False
    await message.answer("Письма загружены, идет проверка 📝")
    for i in range(0, len(emails), 5):
        emails_cut = emails[i:i + 5]
        try:
            ai_answer = await AI.send_to_ai(emails_cut, user.include_prompt, user.exclude_prompt)
            text, empty, for_sms = await AI.save_ai_result(ai_answer, user.telegram_id, save_midle=user.last_saved, )
            if last_checked != -1:
                await set_last_saved(user.telegram_id, last_checked)
            if not (empty):
                any_changes = True
                await message.answer(text, parse_mode="HTML")
        except Exception as e:
            print(f"Ошибка при работе с ии: {e}")
            await message.answer("Произошла ошибка ❌")
    if any_changes:
        await message.answer("Все сообщения проверены ✅")
    else:
        await message.answer("Ничего интересного не найдено ❌")
