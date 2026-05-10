from aiogram.fsm.state import StatesGroup, State


class Profile(StatesGroup):
    waiting_for_email = State()
    waiting_for_password = State()
    waiting_for_phone = State()


class Params(StatesGroup):
    waiting_for_in_prompt = State()
    waiting_for_ex_prompt = State()


class Message_list(StatesGroup):
    waiting_for_del_message = State()
