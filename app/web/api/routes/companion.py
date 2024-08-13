from fastapi import APIRouter
import os
from datetime import datetime
from openai import OpenAI
from app.settings import settings

client = OpenAI(api_key=settings.open_api_key)

router = APIRouter()


@router.get("/companion/greeting")
def companion_greeting() -> None:

    current_time = datetime.now()

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Give a three word greeting welcoming a user named Sunny at the time of day of {current_time}",
            }
        ],
        model="gpt-3.5-turbo",
    )

    return chat_completion.choices[0].message.content

