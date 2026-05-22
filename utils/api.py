"""
Shared API clients for LLM, Etherscan, and DexScreener.
"""

import os
import json
import httpx
from openai import OpenAI


class LLMClient:
    """OpenRouter-backed LLM client using OpenAI SDK."""

    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
        )
        self.model = os.getenv("LLM_MODEL", "google/gemini-2.5-flash")

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """Single-turn LLM call. Returns text response."""
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=1024,
        )
        return resp.choices[0].message.content or ""


class EtherscanClient:
    """Etherscan API client for contract source code and on-chain data."""

    BASE = "https://api.etherscan.io/api"

    def __init__(self):
        self.api_key = os.getenv("ETHERSCAN_API_KEY", "")

    def get_source(self, address: str) -> dict:
        """Get verified contract source code."""
        resp = httpx.get(
            self.BASE,
            params={
                "module": "contract",
                "action": "getsourcecode",
                "address": address,
                "apikey": self.api_key,
            },
            timeout=15,
        )
        data = resp.json()
        if data.get("status") == "1" and data.get("result"):
            item = data["result"][0]
            return {
                "name": item.get("ContractName", ""),
                "compiler": item.get("CompilerVersion", ""),
                "source": item.get("SourceCode", ""),
                "abi": item.get("ABI", ""),
                "proxy": item.get("Proxy", "0"),
                "implementation": item.get("Implementation", ""),
                "verified": item.get("ABI") != "Contract source code not verified",
            }
        return {"verified": False, "error": data.get("message", "unknown")}

    def get_tx_count(self, address: str) -> int:
        """Get transaction count for an address."""
        resp = httpx.get(
            self.BASE,
            params={
                "module": "proxy",
                "action": "eth_getTransactionCount",
                "address": address,
                "tag": "latest",
                "apikey": self.api_key,
            },
            timeout=10,
        )
        result = resp.json().get("result", "0x0")
        return int(result, 16)


class DexScreenerClient:
    """DexScreener API client for token/pair data."""

    BASE = "https://api.dexscreener.com/latest"

    def get_token(self, address: str) -> dict:
        """Get token pairs and market data."""
        resp = httpx.get(
            f"{self.BASE}/tokens/{address}",
            timeout=15,
            headers={"User-Agent": "MultiAgentCryptoResearch/1.0"},
        )
        data = resp.json()
        pairs = data.get("pairs", [])
        if not pairs:
            return {"found": False}

        # Pick highest liquidity pair
        pairs.sort(key=lambda p: float(p.get("liquidity", {}).get("usd", 0) or 0), reverse=True)
        top = pairs[0]

        return {
            "found": True,
            "name": top.get("baseToken", {}).get("name", ""),
            "symbol": top.get("baseToken", {}).get("symbol", ""),
            "price_usd": top.get("priceUsd", "0"),
            "market_cap": top.get("marketCap", 0) or top.get("fdv", 0),
            "liquidity_usd": top.get("liquidity", {}).get("usd", 0),
            "volume_24h": top.get("volume", {}).get("h24", 0),
            "price_change_24h": top.get("priceChange", {}).get("h24", 0),
            "pair_created_at": top.get("pairCreatedAt", 0),
            "dex": top.get("dexId", ""),
            "pair_address": top.get("pairAddress", ""),
            "txns_24h_buys": top.get("txns", {}).get("h24", {}).get("buys", 0),
            "txns_24h_sells": top.get("txns", {}).get("h24", {}).get("sells", 0),
            "info_links": top.get("info", {}).get("websites", []),
            "socials": top.get("info", {}).get("socials", []),
        }
