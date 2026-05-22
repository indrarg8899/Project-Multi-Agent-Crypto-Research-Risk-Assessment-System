"""
Orchestrator — Coordinates parallel agent execution.

Manages the multi-agent pipeline:
1. Launch Contract, Social, Liquidity agents in parallel
2. Feed their outputs to Risk Agent
3. Pass aggregated result to Summary Agent
"""

import asyncio
import time
from typing import Optional

from utils.api import LLMClient, EtherscanClient, DexScreenerClient
from agents import ContractAgent, SocialAgent, LiquidityAgent, RiskAgent, SummaryAgent


class Orchestrator:
    """Multi-agent orchestrator with parallel execution."""

    def __init__(
        self,
        llm: Optional[LLMClient] = None,
        etherscan: Optional[EtherscanClient] = None,
        dexscreener: Optional[DexScreenerClient] = None,
    ):
        self.llm = llm or LLMClient()
        self.etherscan = etherscan or EtherscanClient()
        self.dexscreener = dexscreener or DexScreenerClient()

        # Initialize agents
        self.contract = ContractAgent(self.llm, self.etherscan, self.dexscreener)
        self.social = SocialAgent(self.llm, self.etherscan, self.dexscreener)
        self.liquidity = LiquidityAgent(self.llm, self.etherscan, self.dexscreener)
        self.risk = RiskAgent(self.llm, self.etherscan, self.dexscreener)
        self.summary = SummaryAgent(self.llm, self.etherscan, self.dexscreener)

    async def analyze(self, token_address: str) -> dict:
        """
        Run full multi-agent analysis pipeline.

        Phase 1 (parallel): Contract + Social + Liquidity agents
        Phase 2 (sequential): Risk aggregation
        Phase 3 (sequential): Summary generation

        Returns dict with all agent outputs + final report.
        """
        start = time.time()

        # --- Phase 1: Parallel analysis ---
        print("  [Phase 1] Running 3 agents in parallel...")
        contract_task = asyncio.create_task(self.contract.analyze(token_address))
        social_task = asyncio.create_task(self.social.analyze(token_address))
        liquidity_task = asyncio.create_task(self.liquidity.analyze(token_address))

        contract_result, social_result, liquidity_result = await asyncio.gather(
            contract_task, social_task, liquidity_task
        )

        phase1_time = time.time() - start
        print(f"  [Phase 1] Completed in {phase1_time:.1f}s")
        print(f"    Contract Agent: {contract_result.get('risk_score', '?')}/10")
        print(f"    Social Agent:   {social_result.get('risk_score', '?')}/10")
        print(f"    Liquidity Agent: {liquidity_result.get('risk_score', '?')}/10")

        # --- Phase 2: Risk aggregation ---
        print("  [Phase 2] Aggregating risk signals...")
        risk_result = await self.risk.analyze(
            token_address, contract_result, social_result, liquidity_result
        )

        phase2_time = time.time() - start - phase1_time
        print(f"  [Phase 2] Completed in {phase2_time:.1f}s")
        print(f"    Overall: {risk_result.get('overall_risk_score', '?')}/10")
        print(f"    Verdict: {risk_result.get('verdict', '?')}")

        # --- Phase 3: Summary generation ---
        print("  [Phase 3] Generating report...")
        token_info = self.dexscreener.get_token(token_address)
        report = await self.summary.analyze(
            token_address, token_info, risk_result,
            contract_result, social_result, liquidity_result,
        )

        total_time = time.time() - start
        print(f"  [Phase 3] Completed in {total_time:.1f}s total")

        return {
            "token_address": token_address,
            "token_info": token_info,
            "agent_results": {
                "contract": contract_result,
                "social": social_result,
                "liquidity": liquidity_result,
            },
            "risk_assessment": risk_result,
            "report": report,
            "execution_time": total_time,
        }
