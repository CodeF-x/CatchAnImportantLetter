from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from handlers.common import confirm_message
from keyboards.inline import params_keyboard
from services.ai import AI
from states.input import Params
from database.repository import set_save_midle, get_user_from_db, set_in_prompt, set_ex_prompt, set_user
from services.mail import Mail

router = Router()
load_dotenv()

callback_data = "include_params"
callback_data = "exclude_params"


@router.message(F.text == "⚙️ Параметры")
async def show_params(message: types.Message):
    user = await get_user_from_db(message.from_user.id)
    if user == None:
        await confirm_message(message)
        return
    if user.email_adress != None and user.email_password != None:
        host = Mail.get_imap_host(user.email_adress)
        mail_status = await Mail.check_connection(host, user.email_adress, user.email_password)
    else:
        mail_status = False
    ai_status = await AI.health_check()
    include_text = user.include_prompt if (user.include_prompt != None) else "пусто"
    exclude_text = user.exclude_prompt if (user.exclude_prompt != None) else "пусто"
    save = user.save_midle

    answer = "Параметры:\n\n"
    answer += "<b>почта:</b> " + ("подключена ✅" if (mail_status == True) else "нет подключения ❌") + "\n"
    answer += "<b>нейросеть:</b> " + ("подключена ✅" if (ai_status == True) else "нет подключения ❌") + "\n"
    answer += "<b>сохранять письма средней важности:</b> " + ("✅" if (save == True) else "❌") + "\n"
    answer += "<b>учесть:</b> \n" + include_text + "\n"
    answer += "<b>избегать:</b> \n" + exclude_text + "\n"

    kb = await params_keyboard(save)
    await message.answer(answer, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "refresh_params")
async def refresh_params(callback: types.CallbackQuery):
    user = await get_user_from_db(callback.from_user.id)
    if user == None:
        await confirm_message(callback)
        return
    if user.email_adress != None and user.email_password != None:
        host = Mail.get_imap_host(user.email_adress)
        mail_status = await Mail.check_connection(host, user.email_adress, user.email_password)
    else:
        mail_status = False
    ai_status = await AI.health_check()
    include_text = user.include_prompt if (user.include_prompt != None) else "пусто"
    exclude_text = user.exclude_prompt if (user.exclude_prompt != None) else "пусто"
    save = user.save_midle
    answer = "Параметры:\n\n"
    answer += "<b>почта:</b> " + ("подключена ✅" if (mail_status == True) else "нет подключения ❌") + "\n"
    answer += "<b>нейросеть:</b> " + ("подключена ✅" if (ai_status == True) else "нет подключения ❌") + "\n"
    answer += "<b>сохранять письма средней важности:</b> " + ("✅" if (save == True) else "❌") + "\n"
    answer += "<b>учесть:</b> " + include_text + "\n"
    answer += "<b>избегать:</b> " + exclude_text + "\n"
    kb = await params_keyboard(save)
    await callback.answer("параметры обновлены")
    try:
        await callback.message.edit_text(
            text=answer,
            reply_markup=kb,
            parse_mode="HTML"
        )
    except Exception:
        await callback.answer("что-то пошло не так")


@router.callback_query(F.data == "save_midle")
async def save_midle(callback: types.CallbackQuery):
    user = await get_user_from_db(callback.from_user.id)
    if user == None:
        await confirm_message(callback)
        return
    save = True
    if user.save_midle:
        save = False
    await set_save_midle(callback.from_user.id, save)
    await refresh_params(callback)


@router.callback_query(F.data == "include_params")
async def write_in_params(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user_from_db(callback.from_user.id)
    if user == None:
        await confirm_message(callback)
        return
    await callback.message.answer("Введите темы, которые важны для вас в письмах")
    await state.set_state(Params.waiting_for_in_prompt)
    await callback.answer()


@router.message(Params.waiting_for_in_prompt)
async def get_in_params(message: types.Message, state: FSMContext):
    user = await get_user_from_db(message.from_user.id)
    if user == None:
        await confirm_message(message)
        return
    await set_in_prompt(message.from_user.id, message.text)
    await message.answer("Ваши пожелания учтены")
    await state.clear()


@router.callback_query(F.data == "exclude_params")
async def write_ex_params(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user_from_db(callback.from_user.id)
    if user == None:
        await confirm_message(callback)
        return
    await callback.message.answer("Введите темы, которые вам не так важны в письмах")
    await state.set_state(Params.waiting_for_ex_prompt)
    await callback.answer()


@router.message(Params.waiting_for_ex_prompt)
async def get_ex_params(message: types.Message, state: FSMContext):
    user = await get_user_from_db(message.from_user.id)
    if user == None:
        await confirm_message(message)
        return
    await set_ex_prompt(message.from_user.id, message.text)
    await message.answer("Ваши пожелания учтены")
    await state.clear()
