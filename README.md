# Multi-Agent Crypto Research & Risk Assessment System

An AI-powered multi-agent system that analyzes cryptocurrency tokens in parallel across three dimensions — smart contract safety, social sentiment, and liquidity health — then aggregates signals into a unified risk score with actionable verdicts.

## Architecture

```
User Query (token address)
        ↓
  Intent Classifier
        ↓
  ┌─────┼─────┐
  ↓     ↓     ↓
Contract Social Liquidity
 Agent  Agent   Agent    ← parallel execution
  ↓     ↓     ↓
  └─────┼─────┘
        ↓
  Risk Scoring Agent      ← aggregate + conflict resolution
        ↓
  Summary Agent           ← verdict: GO / WAIT / AVOID
```

## Why Multi-Agent?

| Dimension | Single Model | Multi-Agent |
|-----------|-------------|-------------|
| Speed | Sequential (15-20 min) | Parallel (~45 sec) |
| Accuracy | Reasoning diluted across domains | Specialized prompts per domain |
| Composability | Rewrite for new analysis | Add new agent independently |
| Conflict Handling | Anchored by first finding | Independent signals, aggregated |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API keys
cp .env.example .env
# Edit .env with your keys

# 3. Run analysis
python main.py 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
```

## Agents

| Agent | Role | Data Sources |
|-------|------|-------------|
| **Contract Agent** | Analyze token source code, detect tax/honeypot, verify audit | Etherscan API, on-chain bytecode |
| **Social Agent** | Parse sentiment, detect bots, measure hype | X/Twitter signals, community metrics |
| **Liquidity Agent** | Check pool TVL, depth, holder concentration | DexScreener, on-chain holders |
| **Risk Agent** | Aggregate signals, resolve conflicts, score 1-10 | Internal signals from above agents |
| **Summary Agent** | Generate human-readable verdict | Risk Agent output |

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API key for LLM calls | Yes |
| `ETHERSCAN_API_KEY` | Etherscan API key | Yes |
| `LLM_MODEL` | Model to use (default: `google/gemini-2.5-flash`) | No |

## License

MIT
