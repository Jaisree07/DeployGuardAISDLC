from backend.ai.config import AIConfig


def generate(prompt: str) -> str:
    import ollama  # local import so the package is only required if this path is used

    response = ollama.generate(
        model=AIConfig.OLLAMA_MODEL,
        prompt=prompt,
    )
    return response.get("response", "").strip()