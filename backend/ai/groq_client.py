from backend.ai.config import AIConfig


def generate(prompt: str) -> str:
    if not AIConfig.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not configured")

    from groq import Groq  # local import so the package is only required if this path is used

    client = Groq(api_key=AIConfig.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=AIConfig.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()