from datetime import datetime

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from handlers.common import confirm_message
from keyboards.inline import list_keyboard

from dotenv import load_dotenv

from database.repository import get_all_messages_from_db, del_message, get_user_from_db

from states.input import Message_list

router = Router()
load_dotenv()


@router.message(F.text == "📋 Список важных писем")
async def show_list(message: types.Message):
    user = await get_user_from_db(message.from_user.id)
    if user == None:
        await confirm_message(message)
        return
    answer = "Cписок важных сообщений:\n\n"
    messages = await get_all_messages_from_db(message.from_user.id)
    for item in messages:
        uid = item.uid
        priority = item.priority
        summary = item.summary
        action = item.action_item
        deadline = item.deadline
        answer += f"<b>Номер:</b> {uid}\n"
        if priority == "high":
            answer += "<b>Важность:</b> высокая ‼️\n"
        elif priority == "medium":
            answer += "<b>Важность:</b> средняя ❗\n"
        else:
            answer += "<b>Важность:</b> невероятная ‼️‼️‼️\n"
        answer += f"<b>Срочность:</b> {item.urgency_score} ⏰\n"
        answer += f"<b>Численная важность:</b> {item.importance_score} ⚠️\n"
        answer += f"<b>Содержание:</b> {summary} 🖊\n"
        answer += f"<b>Рекомендация:</b> {action} 📋\n"
        answer += f"<b>Дедлайн:</b> {deadline if (deadline != "None") else "нет"} ⏳\n"
        if (deadline != None and deadline < datetime.now()):
            answer += "<b>Просрочено</b> ❌\n\n"
        else:
            answer += "\n"
    if (answer == "Cписок важных сообщений:\n\n"):
        answer = "Важных сообщений пока нет"
    kb = await list_keyboard()
    await message.answer(answer, parse_mode="HTML", reply_markup=kb)


@router.callback_query(F.data == "delete_message")
async def delete_message(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user_from_db(callback.from_user.id)
    if user == None:
        await confirm_message(callback)
        return
    await callback.message.answer(
        "Введите номер письма, которое нужно удалить")
    await state.set_state(Message_list.waiting_for_del_message)
    await callback.answer()


@router.message(Message_list.waiting_for_del_message)
async def get_in_params(message: types.Message, state: FSMContext):
    user = await get_user_from_db(message.from_user.id)
    if user == None:
        await confirm_message(message)
        return

    try:
        number = int(message.text)
    except:
        await message.answer("Не получилось распознать номер")
        await state.clear()
        return

    messages = await get_all_messages_from_db(message.from_user.id)
    if number in [int(x.uid) for x in messages]:
        await del_message(message.from_user.id, number)
        await message.answer(f"Письмо с номером {number} удалено из списка")
        await state.clear()
        return
    else:
        await message.answer("Такого номера нет")
        await state.clear()
        return
