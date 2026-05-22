"""
Contract Agent — Analyzes smart contract source code for security risks.

Checks:
- Verified source code status
- Sell tax / transfer tax detection
- Honeypot patterns (can buy but can't sell)
- Ownership renouncement status
- Proxy pattern detection
- Known exploit patterns
"""

import json
from .base import BaseAgent

SYSTEM_PROMPT = """You are a smart contract security analyst. Analyze the provided contract data and return a JSON assessment.

You MUST return valid JSON with exactly these fields:
{
  "risk_score": <1-10, where 1=safe, 10=critical>,
  "flags": ["<list of specific red flags found>"],
  "summary": "<2-3 sentence human-readable summary>",
  "tax_info": {"buy_tax": <percent>, "sell_tax": <percent>},
  "is_honeypot": <true/false>,
  "ownership_renounced": <true/false/unknown>,
  "is_proxy": <true/false>
}

Red flags to look for:
- Hidden mint functions (owner can mint unlimited tokens)
- Transfer restrictions (blacklist, pause, max TX limits set by owner)
- Fee manipulation (setFee/setTax can be changed by owner post-deploy)
- Proxy contracts pointing to unaudited implementations
- Unverified source code
- Known exploit patterns (reentrancy, approve race condition)
- Self-destruct capability
- External call to arbitrary addresses

Be thorough but fair. Not all owner privileges are malicious — flag based on severity and exploitability."""


class ContractAgent(BaseAgent):
    """Analyzes token smart contract for security risks."""

    name = "Contract Agent"

    async def analyze(self, token_address: str) -> dict:
        """Analyze contract source code and on-chain state."""
        # Fetch contract source from Etherscan
        contract_data = self.etherscan.get_source(token_address)

        if not contract_data.get("verified"):
            return {
                "risk_score": 8,
                "flags": ["Unverified contract source code"],
                "summary": "Contract source code is not verified on Etherscan. "
                           "Cannot perform security analysis. High risk — "
                           "unverified contracts may contain malicious code.",
                "tax_info": {"buy_tax": -1, "sell_tax": -1},
                "is_honeypot": False,
                "ownership_renounced": "unknown",
                "is_proxy": False,
            }

        # Build analysis prompt with contract data
        source_preview = contract_data.get("source", "")[:6000]  # Limit to ~6K chars
        user_prompt = f"""Analyze this Ethereum smart contract:

Contract Name: {contract_data.get('name', 'Unknown')}
Compiler: {contract_data.get('compiler', 'Unknown')}
Is Proxy: {contract_data.get('proxy') == '1'}
Implementation: {contract_data.get('implementation', 'N/A')}

Source Code (truncated):
```
{source_preview}
```

Provide your security assessment as JSON."""

        result = await self._llm_call(SYSTEM_PROMPT, user_prompt)
        return self._parse_json(result, token_address)
