"""
Base agent class with shared utilities.
"""

import json
import asyncio
from utils.api import LLMClient, EtherscanClient, DexScreenerClient


class BaseAgent:
    """Base class for all analysis agents."""

    name: str = "BaseAgent"

    def __init__(self, llm: LLMClient, etherscan: EtherscanClient, dexscreener: DexScreenerClient):
        self.llm = llm
        self.etherscan = etherscan
        self.dexscreener = dexscreener

    async def analyze(self, token_address: str) -> dict:
        """Override in subclass. Must return dict with at least 'risk_score' and 'summary'."""
        raise NotImplementedError

    async def _llm_call(self, system_prompt: str, user_prompt: str) -> str:
        """Run LLM call in thread pool (OpenAI SDK is sync)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self.llm.chat(system_prompt, user_prompt)
        )

    def _parse_json(self, text: str, token_address: str) -> dict:
        """Parse JSON from LLM response, with fallback."""
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting JSON block from markdown
        if "```" in text:
            parts = text.split("```")
            for part in parts[1::2]:  # Odd indices = code blocks
                cleaned = part.strip()
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()
                try:
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    continue

        # Fallback: return raw text as summary
        return {
            "risk_score": 5,
            "flags": ["Failed to parse structured output"],
            "summary": text[:500],
        }
