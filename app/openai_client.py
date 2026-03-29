import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def chat(system_prompt: str, user_prompt: str, model: str = "gpt-4o") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    if content is None:
        raise ValueError("OpenAI returned empty response content")

    return content