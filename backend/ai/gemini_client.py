import google.generativeai as genai

from backend.ai.config import AIConfig


def generate(prompt: str) -> str:

    if not AIConfig.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    genai.configure(api_key=AIConfig.GEMINI_API_KEY)

    model = genai.GenerativeModel(
        AIConfig.GEMINI_MODEL
    )

    response = model.generate_content(prompt)

    return response.text.strip()