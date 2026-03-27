"""Thin wrapper around the OpenAI chat completions API."""

from openai import OpenAI

from app.config import get_settings


def chat(system: str, user: str) -> str:
    """Send a chat completion request and return the assistant's reply.

    Args:
        system: The system prompt that sets the agent's behaviour and persona.
        user: The user message containing task instructions and context.

    Returns:
        The text content of the model's reply.
    """
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.choices[0].message.content or ""
