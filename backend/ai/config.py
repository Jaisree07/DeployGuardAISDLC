import os
from dotenv import load_dotenv

load_dotenv()


class AIConfig:

    PROVIDER = os.getenv(
        "AI_PROVIDER",
        "groq"
    ).lower()

   
    GROQ_API_KEY = os.getenv(
        "GROQ_API_KEY",
        ""
    )

    GROQ_MODEL = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-20b"
    )

   
    OLLAMA_URL = os.getenv(
        "OLLAMA_URL",
        "http://localhost:11434"
    )

    OLLAMA_MODEL = os.getenv(
        "OLLAMA_MODEL",
        "phi3:mini"
    )

    
    FALLBACK_PROVIDER = os.getenv(
        "AI_FALLBACK_PROVIDER",
        "ollama"
    ).lower()

    FALLBACK_ORDER = [
        FALLBACK_PROVIDER
    ]