import logging

from backend.ai.config import AIConfig
from backend.ai.prompt_builder import build_prompt
from backend.ai import groq_client

logger = logging.getLogger(__name__)

_PROVIDERS = {
    "groq": groq_client.generate
}


class AIService:

    @staticmethod
    def generate(pattern: dict) -> str:
        prompt = build_prompt(pattern)

        order = [AIConfig.PROVIDER] + [
            p for p in AIConfig.FALLBACK_ORDER if p != AIConfig.PROVIDER
        ]

        last_error = None
        for provider_name in order:
            generate_fn = _PROVIDERS.get(provider_name)
            if not generate_fn:
                continue
            try:
                return generate_fn(prompt)
            except Exception as exc:
                logger.warning("AI provider '%s' failed: %s", provider_name, exc)
                last_error = exc
                continue

        # All providers failed — never crash the caller, degrade gracefully
        logger.error("All AI providers failed. Last error: %s", last_error)
        return (
            f"[AI explanation unavailable — all providers failed] "
            f"Raw pattern: {pattern}"
        )

    @staticmethod
    def explain_all(patterns: list) -> list:
        return [
            {"pattern": p, "explanation": AIService.generate(p)}
            for p in patterns
        ]