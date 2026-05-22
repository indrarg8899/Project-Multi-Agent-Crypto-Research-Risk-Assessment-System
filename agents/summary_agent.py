"""
Summary Agent — Generates human-readable verdict report.

Takes the aggregated risk assessment and produces a clear,
actionable summary for the user.
"""

from .base import BaseAgent

SYSTEM_PROMPT = """You are a crypto investment advisor summarizer. You receive a comprehensive risk assessment and produce a clear, actionable report.

Write in a direct, no-BS style. Use emoji sparingly (✅ ⚠️ 🚫 only). Keep it concise.

Format your response as clean text (NOT JSON) with these sections:

**VERDICT: [GO/WAIT/AVOID]**
Risk Score: X/10 | Confidence: XX%

**Summary:** [1-2 sentences]

**Red Flags:**
• [flag 1]
• [flag 2]

**Green Flags (if any):**
• [flag 1]

**Recommendation:** [1-2 sentences on what to do]

**Disclaimer:** This is automated analysis, not financial advice. Always DYOR."""


class SummaryAgent(BaseAgent):
    """Generates human-readable summary from risk assessment."""

    name = "Summary Agent"

    async def analyze(
        self,
        token_address: str,
        token_info: dict,
        risk_result: dict,
        contract_result: dict,
        social_result: dict,
        liquidity_result: dict,
    ) -> str:
        """Generate final human-readable report."""

        user_prompt = f"""Generate a summary report for this token analysis.

Token: {token_info.get('name', 'Unknown')} ({token_info.get('symbol', '?')})
Address: {token_address}
Price: ${token_info.get('price_usd', '0')}
Market Cap: ${token_info.get('market_cap', 0):,.0f}
Liquidity: ${token_info.get('liquidity_usd', 0):,.0f}

## Risk Assessment
Overall Score: {risk_result.get('overall_risk_score', 'N/A')}/10
Verdict: {risk_result.get('verdict', 'N/A')}
Confidence: {risk_result.get('confidence', 'N/A')}
Critical Flags: {risk_result.get('critical_flags', [])}
Reasoning: {risk_result.get('reasoning', 'N/A')}

## Agent Scores
- Contract: {contract_result.get('risk_score', 'N/A')}/10
- Social: {social_result.get('risk_score', 'N/A')}/10
- Liquidity: {liquidity_result.get('risk_score', 'N/A')}/10

## All Flags
Contract: {contract_result.get('flags', [])}
Social: {social_result.get('flags', [])}
Liquidity: {liquidity_result.get('flags', [])}

Generate the summary report."""

        return await self._llm_call(SYSTEM_PROMPT, user_prompt)
