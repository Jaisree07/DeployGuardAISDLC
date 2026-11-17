
import json
import logging

from backend.ai.config import AIConfig
from backend.ai.prompt_builder import build_prompt
from backend.ai import groq_client
from backend.ai import ollama_client

logger = logging.getLogger(__name__)

_PROVIDERS = {
    "groq": groq_client.generate,
    "ollama": ollama_client.generate
}


class AIService:

    @staticmethod
    def _generate_with_prompt(prompt: str, pattern: dict) -> str:
        order = [AIConfig.PROVIDER] + [
            p for p in AIConfig.FALLBACK_ORDER
            if p != AIConfig.PROVIDER
        ]

        last_error = None

        for provider_name in order:
            generate_fn = _PROVIDERS.get(provider_name)

            if not generate_fn:
                continue

            try:
                logger.info("Using AI provider: %s", provider_name)
                return generate_fn(prompt)

            except Exception as exc:
                logger.warning(
                    "AI provider '%s' failed: %s",
                    provider_name,
                    exc
                )
                last_error = exc

        logger.error(
            "All AI providers failed. Last error: %s",
            last_error
        )

        return (
            "[AI explanation unavailable — all providers failed] "
            f"Input data: {pattern}"
        )

    @staticmethod
    def generate(pattern: dict) -> str:
        prompt = build_prompt(pattern)
        return AIService._generate_with_prompt(prompt, pattern)

    @staticmethod
    def generate_ci_insights(pattern: dict) -> str:
        prompt = f"""
You are DeployGuard AI, an experienced DevOps and CI/CD reliability assistant.

Analyze the supplied GitHub Actions pipeline execution data.

Provide a concise, evidence-based explanation using these sections:

1. Pipeline Health Summary
2. Key Observations
3. Failure Analysis
4. Recommended Actions

Rules:
- Use only the supplied data.
- Do not invent error messages, root causes, or deployment impacts.
- Distinguish controlled test failures from unexpected failures.
- Do not describe a controlled test failure as a production incident.
- If the available data cannot establish a root cause, explicitly say so.
- Mention success rate and execution duration where available.
- Keep the response understandable to a non-expert engineer.

Pipeline data:
{json.dumps(pattern, indent=2, default=str)}
"""
        return AIService._generate_with_prompt(prompt, pattern)

    @staticmethod
    def explain_all(patterns: list) -> list:
        return [
            {
                "pattern": p,
                "explanation": AIService.generate(p)
            }
            for p in patterns
        ]
