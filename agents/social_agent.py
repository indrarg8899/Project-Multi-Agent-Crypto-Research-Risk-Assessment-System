"""
Social Agent — Analyzes social sentiment and community signals.

Checks:
- Social media presence (X/Twitter, Telegram, website)
- Community engagement metrics
- Bot/spam detection indicators
- Influencer activity patterns
- Hype-to-substance ratio
"""

from .base import BaseAgent

SYSTEM_PROMPT = """You are a crypto social sentiment analyst. Analyze the provided social/community data and return a JSON assessment.

You MUST return valid JSON with exactly these fields:
{
  "risk_score": <1-10, where 1=organic/healthy, 10=fake/scam>,
  "flags": ["<list of specific red flags>"],
  "summary": "<2-3 sentence summary>",
  "sentiment": "<positive/neutral/negative>",
  "bot_risk": <1-10, where 1=organic, 10=heavily botted>,
  "hype_score": <1-10, where 1=minimal hype, 10=extreme hype with no substance>
}

Red flags to look for:
- No social links at all (anonymous team, no community)
- Very new social accounts (< 30 days old)
- Low engagement relative to follower count
- Generic/copied project descriptions
- No website or broken links
- All social accounts created around same time
- Volume spike without corresponding social activity increase
- Buy/sell ratio heavily skewed (possible wash trading)

Be fair — new projects naturally have smaller communities. Score based on deception signals, not size."""


class SocialAgent(BaseAgent):
    """Analyzes social presence and sentiment for a token project."""

    name = "Social Agent"

    async def analyze(self, token_address: str) -> dict:
        """Analyze social signals from DexScreener and on-chain data."""
        # Get token data including social links
        token_data = self.dexscreener.get_token(token_address)

        if not token_data.get("found"):
            return {
                "risk_score": 7,
                "flags": ["Token not found on DexScreener", "No trading pairs exist"],
                "summary": "Token has no trading pairs on any tracked DEX. "
                           "Either very new, not yet launched, or non-existent.",
                "sentiment": "unknown",
                "bot_risk": 5,
                "hype_score": 1,
            }

        # Build analysis prompt
        socials = token_data.get("socials", [])
        links = token_data.get("info_links", [])
        txns = token_data

        user_prompt = f"""Analyze the social signals for this token:

Name: {token_data.get('name', 'Unknown')} ({token_data.get('symbol', '?')})
DEX: {token_data.get('dex', 'Unknown')}
Market Cap: ${token_data.get('market_cap', 0):,.0f}
24h Volume: ${token_data.get('volume_24h', 0):,.0f}
24h Price Change: {token_data.get('price_change_24h', 0)}%
Buy/Sell Ratio (24h): {txns.get('txns_24h_buys', 0)} buys / {txns.get('txns_24h_sells', 0)} sells
Pair Age: Created at timestamp {token_data.get('pair_created_at', 0)}

Social Links: {socials}
Website Links: {links}

Provide your social sentiment assessment as JSON."""

        result = await self._llm_call(SYSTEM_PROMPT, user_prompt)
        return self._parse_json(result, token_address)
