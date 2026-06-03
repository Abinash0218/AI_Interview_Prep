import logging
import time
from typing import List, Dict, Optional

from backend.config import get_settings
from backend.prompts import CATEGORY_PROMPTS

logger = logging.getLogger(__name__)
settings = get_settings()

MAX_RETRIES = 3
RETRY_DELAY = 1.0


def _build_messages(system_prompt: str, history: List[Dict[str, str]], user_message: str) -> list:
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        role = msg["role"]
        if role == "assistant":
            role = "assistant"
        elif role == "user":
            role = "user"
        else:
            continue
        messages.append({"role": role, "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})
    return messages


def _call_gemini(system_prompt: str, history: List[Dict[str, str]], user_message: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt,
    )

    chat_history = []
    for msg in history:
        if msg["role"] in ("user", "assistant"):
            chat_history.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [msg["content"]],
            })

    chat = model.start_chat(history=chat_history)
    response = chat.send_message(user_message)
    return response.text


def _call_groq(system_prompt: str, history: List[Dict[str, str]], user_message: str) -> str:
    from groq import Groq

    client = Groq(api_key=settings.GROQ_API_KEY)
    messages = _build_messages(system_prompt, history, user_message)
    openai_messages = []
    for m in messages:
        if m["role"] == "system":
            openai_messages.append({"role": "system", "content": m["content"]})
        else:
            openai_messages.append({"role": m["role"], "content": m["content"]})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=openai_messages,
        max_tokens=4096,
        temperature=0.7,
    )
    return response.choices[0].message.content


def generate_response(
    category: str,
    history: List[Dict[str, str]],
    user_message: str,
    preferred_model: str = "gemini",
) -> str:
    system_prompt = CATEGORY_PROMPTS.get(category, CATEGORY_PROMPTS["technical_interview"])
    last_error: Optional[Exception] = None

    for attempt in range(MAX_RETRIES):
        try:
            if preferred_model == "groq" and settings.GROQ_API_KEY:
                return _call_groq(system_prompt, history, user_message)
            if settings.GEMINI_API_KEY:
                return _call_gemini(system_prompt, history, user_message)
            if settings.GROQ_API_KEY:
                return _call_groq(system_prompt, history, user_message)
            raise ValueError("No AI API key configured. Set GEMINI_API_KEY or GROQ_API_KEY in .env")
        except Exception as e:
            last_error = e
            logger.warning("AI call attempt %d failed: %s", attempt + 1, str(e))
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            if settings.GROQ_API_KEY and preferred_model != "groq":
                try:
                    return _call_groq(system_prompt, history, user_message)
                except Exception as groq_err:
                    logger.warning("Groq fallback failed: %s", str(groq_err))

    logger.error("All AI attempts failed: %s", last_error)
    raise RuntimeError(f"AI service unavailable: {last_error}")
