import os
from dotenv import load_dotenv

load_dotenv()


class AIConfig:

    # Active AI Provider
    PROVIDER = os.getenv("AI_PROVIDER", "groq").lower()

    # -----------------------------
    # Groq Configuration
    # -----------------------------
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

    GROQ_MODEL = os.getenv(
        "GROQ_MODEL",
        "llama-3.1-8b-instant"
    )

    # -----------------------------
    # Optional Ollama Configuration
    # (Keep for future local AI support)
    # -----------------------------
    OLLAMA_URL = os.getenv(
        "OLLAMA_URL",
        "http://localhost:11434/api/generate"
    )

    OLLAMA_MODEL = os.getenv(
        "OLLAMA_MODEL",
        "llama3"
    )

    # -----------------------------
    # Provider Fallback Order
    # -----------------------------
    FALLBACK_ORDER = [
        "groq"
    ]