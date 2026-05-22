"""
Risk Agent — Aggregates signals from all analysis agents.

Takes outputs from Contract, Social, and Liquidity agents,
resolves conflicts, and produces a unified risk score.
"""

from .base import BaseAgent

SYSTEM_PROMPT = """You are a crypto risk assessment aggregator. You receive analysis results from three specialized agents: Contract Agent (smart contract security), Social Agent (community/sentiment), and Liquidity Agent (pool health).

Your job is to:
1. Weight and combine their risk scores into a unified score
2. Resolve conflicts between agents (e.g., contract looks safe but liquidity is thin)
3. Identify the most critical risk factors
4. Produce a final verdict

You MUST return valid JSON with exactly these fields:
{
  "overall_risk_score": <1-10, weighted average with adjustments>,
  "verdict": "<GO | WAIT | AVOID>",
  "confidence": <0.0-1.0, how confident in this verdict>,
  "critical_flags": ["<top 3 most important flags across all agents>"],
  "summary": "<3-4 sentence executive summary>",
  "reasoning": "<brief explanation of how scores were weighted and any conflicts resolved>"
}

Weighting rules:
- Contract Agent score weight: 0.40 (most important — code is truth)
- Liquidity Agent score weight: 0.35 (rug pulls happen via liquidity)
- Social Agent score weight: 0.25 (social can be faked, less reliable)

Verdict rules:
- Overall score 1-3: GO (low risk, proceed with normal caution)
- Overall score 4-6: WAIT (moderate risk, research more before entering)
- Overall score 7-10: AVOID (high risk, likely scam or dangerous)

Conflict resolution:
- If any single agent scores >= 9 (critical), cap overall at minimum 7 regardless of others
- If contract is unverified (score 8+), add +1 to overall regardless of other scores
- If liquidity < $10K AND token < 7 days old, add +1 to overall"""


class RiskAgent(BaseAgent):
    """Aggregates multi-agent signals into unified risk assessment."""

    name = "Risk Agent"

    async def analyze(
        self,
        token_address: str,
        contract_result: dict,
        social_result: dict,
        liquidity_result: dict,
    ) -> dict:
        """Combine all agent outputs into unified risk score."""

        user_prompt = f"""Aggregate these three agent analyses into a unified risk assessment.

## Contract Agent Analysis
Risk Score: {contract_result.get('risk_score', 'N/A')}/10
Flags: {contract_result.get('flags', [])}
Summary: {contract_result.get('summary', 'N/A')}
Tax Info: {contract_result.get('tax_info', {})}
Is Honeypot: {contract_result.get('is_honeypot', 'unknown')}

## Social Agent Analysis
Risk Score: {social_result.get('risk_score', 'N/A')}/10
Flags: {social_result.get('flags', [])}
Summary: {social_result.get('summary', 'N/A')}
Sentiment: {social_result.get('sentiment', 'unknown')}
Bot Risk: {social_result.get('bot_risk', 'N/A')}/10

## Liquidity Agent Analysis
Risk Score: {liquidity_result.get('risk_score', 'N/A')}/10
Flags: {liquidity_result.get('flags', [])}
Summary: {liquidity_result.get('summary', 'N/A')}
Liquidity Grade: {liquidity_result.get('liquidity_grade', 'N/A')}
Rug Risk: {liquidity_result.get('rug_risk', 'N/A')}/10

Provide your aggregated risk assessment as JSON."""

        result = await self._llm_call(SYSTEM_PROMPT, user_prompt)
        return self._parse_json(result, token_address)
