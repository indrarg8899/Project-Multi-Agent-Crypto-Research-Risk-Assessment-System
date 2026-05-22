#!/usr/bin/env python3
"""
Multi-Agent Crypto Research & Risk Assessment System

Usage:
    python main.py <token_address>
    python main.py 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
"""

import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

from orchestrator import Orchestrator


async def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <token_address>")
        print("Example: python main.py 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984")
        sys.exit(1)

    token_address = sys.argv[1].strip()

    # Validate address format
    if not token_address.startswith("0x") or len(token_address) != 42:
        print(f"Error: Invalid Ethereum address: {token_address}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  Multi-Agent Crypto Research")
    print(f"  Token: {token_address}")
    print(f"{'='*60}\n")

    orchestrator = Orchestrator()
    result = await orchestrator.analyze(token_address)

    # Print final report
    print(f"\n{'='*60}")
    print(f"  FINAL REPORT")
    print(f"{'='*60}\n")
    print(result["report"])
    print(f"\n{'='*60}")
    print(f"  Analysis completed in {result['execution_time']:.1f}s")
    print(f"{'='*60}\n")

    # Print structured data summary
    risk = result["risk_assessment"]
    print(f"Structured Output:")
    print(f"  Overall Risk Score: {risk.get('overall_risk_score', 'N/A')}/10")
    print(f"  Verdict: {risk.get('verdict', 'N/A')}")
    print(f"  Confidence: {risk.get('confidence', 'N/A')}")
    print(f"  Critical Flags: {risk.get('critical_flags', [])}")


if __name__ == "__main__":
    asyncio.run(main())
