import os

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from keyboards.inline import password_instruction, phone_del_keyboard
from keyboards.reply import phone_keyboard, main_menu
from states.input import Profile
from database.repository import set_email, get_user_from_db, set_phone, set_password, set_last_saved, set_consent, \
    set_user
from database.security import decrypt_data
from services.mail import Mail

router = Router()
load_dotenv()

domains = ['@gmail.com', '@yandex.ru', '@yandex.by', '@mail.ru', '@list.ru', '@bk.ru', '@inbox.ru', '@outlook.com',
           '@icloud.com']


def fix_number(number: str):
    fixed_number = "".join(x for x in number if x.isdigit())
    return fixed_number


@router.callback_query(F.data == "change_email")
async def start_add_mail(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ваш адрес почты (например, example@yandex.ru):")
    await state.set_state(Profile.waiting_for_email)
    await callback.answer()


@router.message(Profile.waiting_for_email)
async def get_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    correct_email = False
    for x in domains:
        if x in email:
            correct_email = True;
    if not (correct_email):
        await message.answer("Некорректная почта, доступные домены: " + ", ".join(domains))
        await state.clear()
        return
    await set_email(message.from_user.id, email)
    try:
        user = await get_user_from_db(message.from_user.id)
        if (user.email_adress != None and user.email_password != None):
            host = Mail.get_imap_host(user.email_adress)
            uid = await Mail.get_last_id(host, user.email_adress, user.email_password)
            await set_last_saved(message.from_user.id, uid)
    except Exception as e:
        print(f"Ошибка при работе с почтой: {e}")
    await message.answer("Новая почта сохранена")
    await state.clear()


@router.callback_query(F.data == "change_password")
async def start_add_mail(callback: types.CallbackQuery, state: FSMContext):
    kb = await password_instruction()
    await callback.message.answer(
        "Введите пароль приложения (НЕ пароль от вашего аккаунта. Для получения инструкции, " +
        "как получить пароль приложения, нажмите на кнопку)", reply_markup=kb)
    await state.set_state(Profile.waiting_for_password)
    await callback.answer()


@router.message(Profile.waiting_for_password)
async def get_password(message: types.Message, state: FSMContext):
    await set_password(message.from_user.id, message.text.strip())
    try:
        user = await get_user_from_db(message.from_user.id)
        if (user.email_adress != None and user.email_password != None):
            host = Mail.get_imap_host(user.email_adress)
            uid = await Mail.get_last_id(host, user.email_adress, user.email_password)
            if uid != -1:
                await set_last_saved(message.from_user.id, uid)
    except Exception as e:
        print(f"Ошибка при работе с почтой: {e}")
    await message.answer("Новый пароль сохранен")
    await state.clear()


@router.callback_query(F.data == "change_phone")
async def start_add_mail(callback: types.CallbackQuery, state: FSMContext):
    builder = await phone_keyboard()
    answer = await callback.message.answer(
        f'Нажимая кнопку «Отправить номер», вы подтверждаете свое <a href="{os.getenv("AGREEMENT")}">согласие на получение'
        ' информационных рассылок и обработку персональных данных</a>',
        reply_markup=builder, parse_mode="HTML",
        disable_web_page_preview=True)
    kb = await phone_del_keyboard()
    await callback.message.answer(
        "Выберите дествие:",
        reply_markup=kb
    )
    await callback.answer()
    await state.set_state(Profile.waiting_for_phone)


@router.message(Profile.waiting_for_phone, F.contact)
async def handle_contact(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    user_id = message.from_user.id
    await set_consent(user_id, phone, "GRANTED", "2026/v1")
    await set_phone(user_id, fix_number(phone))
    await message.answer(f"Спасибо! Номер {phone} подтвержден. Теперь вы будете получать уведомления.",
                         reply_markup=main_menu)
    await state.clear()


@router.callback_query(Profile.waiting_for_phone, F.data == "close_number")
async def handle_contact(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    user = await get_user_from_db(user_id)
    if user == None:
        await set_user(callback.from_user.id)
        user = await get_user_from_db(callback.from_user.id)
    if user.phone_number != None:
        await set_consent(user_id, user.phone_number, "REVOKED", "2026/v1")
    await set_phone(user_id, None)
    await callback.message.answer(f"Номер удален.", reply_markup=main_menu)
    await state.clear()


@router.callback_query(F.data == "refresh_profile")
async def refresh_profile_handler(callback: types.CallbackQuery):
    user = await get_user_from_db(callback.from_user.id)
    if user == None:
        await set_user(callback.from_user.id)
        user = await get_user_from_db(callback.from_user.id)
    answer = "Настройки:\n\n"
    answer += "<b>почта:</b> <u>" + (
        str(decrypt_data(user.email_adress)) if (user.email_adress != None) else "не задана") + "</u>\n"
    answer += "<b>пароль:</b> <u>" + ("скрыт" if (user.email_adress != None) else "не задан") + "</u>\n"
    answer += "<b>телефон:</b> <u>" + (
        str(decrypt_data(user.phone_number)) if (user.phone_number != None) else "не задан") + "</u>\n"
    try:
        await callback.message.edit_text(
            text=answer,
            reply_markup=callback.message.reply_markup,
            parse_mode="HTML"
        )
    except Exception:
        await callback.answer("Данные уже актуальны")
    await callback.answer()
