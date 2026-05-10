import logging

from database.repository import get_all_active_users_from_db, set_last_saved
from services.SMSService import SMSService
from services.mail import Mail
from services.ai import AI
from aiogram import Bot


async def check_emails_job(bot: Bot):
    users = await get_all_active_users_from_db()
    for user in users:
        host = Mail.get_imap_host(user.email_adress)
        emails, last_checked = await Mail.fetch_latest_unread(host, user.email_adress, user.email_password,
                                                              user.last_saved)
        for i in range(0, len(emails), 5):
            emails_cut = emails[i:i + 5]
            try:
                ai_answer = await AI.send_to_ai(emails_cut, user.include_prompt, user.exclude_prompt)
                text, empty, extreme = await AI.save_ai_result(ai_answer, user.telegram_id, save_midle=user.last_saved)
                if not (empty):
                    await bot.send_message(user.telegram_id, text, parse_mode="HTML")
                    if extreme:
                        await SMSService.send(user.phone_number)
            except Exception as e:
                logging.getLogger(__name__).error(e)
                return
        if last_checked != -1:
            await set_last_saved(user.telegram_id, last_checked)
