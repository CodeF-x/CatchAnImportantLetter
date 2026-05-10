from datetime import datetime

from sqlalchemy import select, update, delete
from database.models import async_session, User, Message, Consent, Politics_consent
from sqlalchemy.dialects.postgresql import insert
from database.security import encrypt_data, decrypt_data


async def get_user_from_db(user_id):
    async with async_session() as session:
        query = select(User).where(User.telegram_id == user_id)

        result = await session.execute(query)

        user = result.scalar_one_or_none()
        if user != None:
            user.exclude_prompt = decrypt_data(user.exclude_prompt)
            user.include_prompt = decrypt_data(user.include_prompt)
            user.email_adress = decrypt_data(user.email_adress)
            user.email_password = decrypt_data(user.email_password)
            user.phone_number = decrypt_data(user.phone_number)
        return user


async def get_all_active_users_from_db():
    async with async_session() as session:
        query = select(User).where(
            User.email_adress.is_not(None),
            User.email_password.is_not(None)
        )

        result = await session.execute(query)

        users = result.scalars().all()
        for user in users:
            user.exclude_prompt = decrypt_data(user.exclude_prompt)
            user.include_prompt = decrypt_data(user.include_prompt)
            user.email_adress = decrypt_data(user.email_adress)
            user.email_password = decrypt_data(user.email_password)
            user.phone_number = decrypt_data(user.phone_number)
        return users


async def set_user(tg_id):
    async with async_session() as session:
        stmt = insert(User).values(
            telegram_id=tg_id
        )

        stmt = stmt.on_conflict_do_nothing(index_elements=['telegram_id'])

        await session.execute(stmt)
        await session.commit()


async def del_user(tg_id):
    async with async_session() as session:
        stmt = (
            delete(User)
            .where(User.telegram_id == tg_id)
        )
        await session.execute(stmt)
        await session.commit()


async def set_consent(telegram_id, phone_number, action, consent_text_version):
    async with async_session() as session:
        stmt = insert(Consent).values(
            telegram_id=telegram_id,
            phone_number=phone_number,
            action=action,
            consent_text_version=consent_text_version
        )

        await session.execute(stmt)
        await session.commit()


async def set_politics_consent(telegram_id, action, consent_text_version):
    async with async_session() as session:
        stmt = insert(Politics_consent).values(
            telegram_id=telegram_id,
            action=action,
            consent_text_version=consent_text_version
        )

        await session.execute(stmt)
        await session.commit()


async def set_email(tg_id, email):
    async with async_session() as session:
        encrypted = encrypt_data(email)
        stmt = (
            update(User)
            .where(User.telegram_id == tg_id)
            .values(email_adress=encrypted)
        )
        await session.execute(stmt)
        await session.commit()


async def set_in_prompt(tg_id, text):
    async with async_session() as session:
        encrypted = encrypt_data(text)
        stmt = (
            update(User)
            .where(User.telegram_id == tg_id)
            .values(include_prompt=encrypted)
        )
        await session.execute(stmt)
        await session.commit()


async def set_ex_prompt(tg_id, text):
    async with async_session() as session:
        encrypted = encrypt_data(text)
        stmt = (
            update(User)
            .where(User.telegram_id == tg_id)
            .values(exclude_prompt=encrypted)
        )
        await session.execute(stmt)
        await session.commit()


async def set_save_midle(tg_id, save):
    async with async_session() as session:
        stmt = (
            update(User)
            .where(User.telegram_id == tg_id)
            .values(save_midle=save)
        )
        await session.execute(stmt)
        await session.commit()


async def set_password(tg_id, password):
    async with async_session() as session:
        encrypted = encrypt_data(password)
        stmt = (
            update(User)
            .where(User.telegram_id == tg_id)
            .values(email_password=encrypted)
        )
        await session.execute(stmt)
        await session.commit()


async def set_phone(tg_id, phone):
    async with async_session() as session:
        encrypted = encrypt_data(phone)
        stmt = (
            update(User)
            .where(User.telegram_id == tg_id)
            .values(phone_number=encrypted)
        )
        await session.execute(stmt)
        await session.commit()


async def set_last_saved(tg_id, last_saved):
    async with async_session() as session:
        stmt = (
            update(User)
            .where(User.telegram_id == tg_id)
            .values(last_saved=last_saved)
        )
        await session.execute(stmt)
        await session.commit()


async def save_message(tg_id, uid, priority, importance_score, urgency_score, summary, action_item, deadline: datetime):
    async with async_session() as session:
        encrypted_summary = encrypt_data(summary)
        encrypted_action_item = encrypt_data(action_item)
        stmt = insert(Message).values(
            user_id=tg_id,
            uid=uid,
            priority=priority,
            importance_score=importance_score,
            urgency_score=urgency_score,
            summary=encrypted_summary,
            action_item=encrypted_action_item,
            deadline=deadline,
        )

        await session.execute(stmt)
        await session.commit()


async def del_message(tg_id, uid):
    async with async_session() as session:
        stmt = (
            delete(Message)
            .where(Message.user_id == tg_id, Message.uid == uid)
        )
        await session.execute(stmt)
        await session.commit()


async def get_message_from_db(id):
    async with async_session() as session:
        query = select(Message).where(Message.id == id)

        result = await session.execute(query)

        message = result.scalar_one_or_none()

        if message != None:
            message.summary = decrypt_data(message.summary)
            message.action_item = decrypt_data(message.action_item)

        return message


async def get_all_messages_from_db(user_id):
    async with async_session() as session:
        query = select(Message).where(Message.user_id == user_id)

        result = await session.execute(query)

        messages = result.scalars().all()

        for message in messages:
            message.summary = decrypt_data(message.summary)
            message.action_item = decrypt_data(message.action_item)
        return messages
