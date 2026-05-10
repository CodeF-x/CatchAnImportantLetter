from imap_tools import MailBox, AND

IMAP_PROVIDERS = {
    'gmail.com': 'imap.gmail.com',
    'yandex.ru': 'imap.yandex.ru',
    'yandex.by': 'imap.yandex.ru',
    'mail.ru': 'imap.mail.ru',
    'list.ru': 'imap.mail.ru',
    'bk.ru': 'imap.mail.ru',
    'inbox.ru': 'imap.mail.ru',
    'outlook.com': 'outlook.office365.com',
    'icloud.com': 'imap.mail.me.com'
}


class Mail:
    @staticmethod
    async def fetch_latest_unread(host, user, password, last_saved):
        emails = []
        last_checked = -1
        try:
            with MailBox(host).login(user, password, 'INBOX') as mailbox:
                criteria = AND(seen=False)
                for msg in mailbox.fetch(criteria, reverse=True, mark_seen=False):
                    uid = int(msg.uid)
                    if uid <= last_saved:
                        break
                    last_checked = max(last_checked, uid)
                    emails.append({
                        "uid": int(msg.uid),
                        "subject": msg.subject,
                        "text": (msg.text or msg.html)[:500],
                        "date": msg.date
                    })
        except Exception as e:
            print(f"Ошибка при работе с почтой: {e}")
        return emails, last_checked

    @staticmethod
    def get_imap_host(email_address):
        domain = email_address.lower().split('@')[-1]
        return IMAP_PROVIDERS.get(domain)

    @staticmethod
    async def get_last_id(host, user, password):
        last_uid = -1
        try:
            with MailBox(host).login(user, password, 'INBOX') as mailbox:
                msg = next(mailbox.fetch(limit=1, reverse=True), None)
                last_uid = int(msg.uid) if msg else -1
        except Exception as e:
            print(f"Ошибка при работе с почтой: {e}")
        return last_uid

    @staticmethod
    async def check_connection(host, user, password):
        try:
            with MailBox(host).login(user, password, 'INBOX'):
                pass
            return True
        except Exception:
            return False
