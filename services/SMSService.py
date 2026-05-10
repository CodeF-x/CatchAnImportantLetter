import logging
import os

import httpx
from dotenv import load_dotenv

load_dotenv()


class SMSService:
    API = os.getenv("SMS_API")
    EMAIL = os.getenv("SMS_EMAIL")

    @classmethod
    async def send(self, phone):
        URL = f"https://{self.EMAIL}:{self.API}@gate.smsaero.ru/v2/sms/send"
        text = "Пришло важное сообшение!"
        params = {
            "number": phone,
            "text": text,
            "sign": "SMS Aero",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(URL, params=params)
                res = response.json()
                if res.get("success"):
                    return True
                else:
                    return False
            except Exception as e:
                logging.getLogger(__name__).error(f"Ошибка сети: {e}")
                return False
