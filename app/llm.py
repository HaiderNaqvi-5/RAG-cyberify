from openai import OpenAI

from app.config import OPENAI_API_KEY, CHAT_MODEL


client = OpenAI(api_key=OPENAI_API_KEY)


def chat(system_prompt: str, user_prompt: str) -> str:

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()