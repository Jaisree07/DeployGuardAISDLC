from backend.ai.config import AIConfig


def generate(prompt: str) -> str:
    import ollama

    client = ollama.Client(
        host=AIConfig.OLLAMA_URL
    )

    response = client.generate(
        model=AIConfig.OLLAMA_MODEL,
        prompt=prompt,
    )

    return response.get("response", "").strip()