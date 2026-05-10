import json
import os

import openai
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from database.repository import save_message

load_dotenv()
class AI:
    @staticmethod
    def system_prompt(current_time, in_prompt, ex_prompt):
        return f"""Ты — интеллектуальный почтовый ассистент. 
            Текущее время: {current_time}
            
            Твоя задача: 
            1. Проанализировать входящие письма.
            2. Определить важность (0-10) и срочность (0-10).
            3. Игнорировать спам или ставить ему минимальный приоритет.
            
            Верни результат строго в формате JSON:
            {{
              "analysis": [
                {{
                  "uid": "int",
                  "priority": "extreme/high/medium/low",
                  "score": {{"importance": 0, "urgency": 0}},
                  "summary": "краткая суть",
                  "action": "рекомендация",
                  "date": "дата дедлайна(в формате datetime)/None"
                }}
              ]
            }}
            extreme выбирай если осталось меньше часа(и оно довольно важное) или в письме что-то очень важное.
            Учти пожелания пользователя, используй и прислушивайся к его предпочтениям, и используй свой анализ
            Он считает важным: {in_prompt}
            Он считает не важным: {ex_prompt}
"""

    @staticmethod
    async def send_to_ai(emails, in_prompt, ex_prompt):
        now = datetime.now(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S")

        user_content = f"Проанализируй письма:\n{emails}"
        client = openai.OpenAI(
            api_key=os.getenv("AI_API"),
            base_url=os.getenv("AI_LINK")
        )

        response = client.chat.completions.create(
            model=os.getenv("AI_MODEL"),
            messages=[
                {"role": "system", "content": AI.system_prompt(now, in_prompt, ex_prompt)},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        return response.choices[0].message.content

    @staticmethod
    async def save_ai_result(response_text, user_id, save_midle):
        data = json.loads(response_text)
        analysis_list = data.get("analysis", [])
        answer = "Интересные сообщения:\n\n"
        extreme = False
        for item in analysis_list:
            uid = item['uid']
            priority = item['priority']
            if not (priority in "medium high extreme") or (priority == "medium" and not (save_midle)):
                continue
            summary = item['summary']
            action = item['action']
            deadline = item['date']
            try:
                clear_date = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    clear_date = datetime.strptime(deadline.split(' ')[0], "%Y-%m-%d")
                except:
                    clear_date = None
            if priority == "medium":
                answer += "<b>Важность:</b> средняя ❗\n"
            elif priority == "high":
                answer += "<b>Важность:</b> высокая ‼️\n"
            else:
                extreme = True
                answer += "<b>Важность:</b> невероятная ‼️‼️‼️\n"
            answer += f"<b>Срочность:</b> {item['score']['urgency']} ⏰\n"
            answer += f"<b>Численная важность:</b> {item['score']['importance']} ⚠️\n"
            answer += f"<b>Содержание:</b> {summary} 🖊\n"
            answer += f"<b>Рекомендация:</b> {action} 📋\n"
            answer += f"<b>Дедлайн:</b> {deadline if (deadline != "None") else "нет"} ⏳\n\n"

            await save_message(user_id, uid, priority, item['score']['importance'], item['score']['urgency'],
                               summary, action, clear_date)

        if (answer == "Интересные сообщения:\n\n"):
            return "Все сообщения уже были просмотрены", True, extreme

        return answer, False, extreme

    @staticmethod
    async def health_check():
        client = openai.OpenAI(
            api_key=os.getenv("AI_API"),
            base_url=os.getenv("AI_LINK")
        )
        if (client.models.list() != []):
            return True
        else:
            return False
