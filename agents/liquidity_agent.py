"""
Liquidity Agent — Analyzes pool health and holder distribution.

Checks:
- Pool liquidity depth (TVL)
- Liquidity lock status
- Top holder concentration
- Volume-to-liquidity ratio
- Trading activity patterns
"""

from .base import BaseAgent

SYSTEM_PROMPT = """You are a DeFi liquidity analyst. Analyze the provided market data and return a JSON assessment.

You MUST return valid JSON with exactly these fields:
{
  "risk_score": <1-10, where 1=deep/healthy liquidity, 10=thin/rug-pull risk>,
  "flags": ["<list of specific red flags>"],
  "summary": "<2-3 sentence summary>",
  "liquidity_grade": "<A/B/C/D/F>",
  "rug_risk": <1-10, where 1=low, 10=imminent>,
  "whale_concentration": <1-10, where 1=well-distributed, 10=heavily concentrated>
}

Red flags to look for:
- Very low liquidity (< $50K) — easy to manipulate price
- Extremely high volume-to-liquidity ratio (> 10x) — possible wash trading
- Very new pair (< 24 hours) with high volume — pump & dump pattern
- Single large holder owning > 20% of supply
- Liquidity not locked or no lock proof
- Sudden liquidity removal (if detectable)
- Buy/sell imbalance (> 80% buys = possible accumulation for dump)

Scoring guidelines:
- TVL > $1M + established pair (> 30 days) = score 1-3
- TVL $100K-$1M + 7-30 days old = score 3-5
- TVL $10K-$100K + < 7 days = score 5-7
- TVL < $10K or brand new = score 7-10"""


class LiquidityAgent(BaseAgent):
    """Analyzes liquidity health and trading patterns."""

    name = "Liquidity Agent"

    async def analyze(self, token_address: str) -> dict:
        """Analyze liquidity from DexScreener market data."""
        token_data = self.dexscreener.get_token(token_address)

        if not token_data.get("found"):
            return {
                "risk_score": 9,
                "flags": ["No liquidity pool found"],
                "summary": "No trading pairs exist for this token. "
                           "Cannot assess liquidity. Maximum risk.",
                "liquidity_grade": "F",
                "rug_risk": 10,
                "whale_concentration": 10,
            }

        # Calculate derived metrics
        liq = float(token_data.get("liquidity_usd", 0) or 0)
        vol = float(token_data.get("volume_24h", 0) or 0)
        buys = token_data.get("txns_24h_buys", 0) or 0
        sells = token_data.get("txns_24h_sells", 0) or 0
        vol_liq_ratio = vol / liq if liq > 0 else 0
        buy_pct = buys / (buys + sells) * 100 if (buys + sells) > 0 else 50

        user_prompt = f"""Analyze the liquidity profile for this token:

Name: {token_data.get('name', 'Unknown')} ({token_data.get('symbol', '?')})
DEX: {token_data.get('dex', 'Unknown')}
Price: ${token_data.get('price_usd', '0')}
Market Cap: ${token_data.get('market_cap', 0):,.0f}
Liquidity (TVL): ${liq:,.0f}
24h Volume: ${vol:,.0f}
Volume/Liquidity Ratio: {vol_liq_ratio:.2f}x
24h Buys: {buys} | 24h Sells: {sells}
Buy Pressure: {buy_pct:.1f}%
Price Change 24h: {token_data.get('price_change_24h', 0)}%
Pair Address: {token_data.get('pair_address', 'N/A')}

Provide your liquidity assessment as JSON."""

        result = await self._llm_call(SYSTEM_PROMPT, user_prompt)
        return self._parse_json(result, token_address)
