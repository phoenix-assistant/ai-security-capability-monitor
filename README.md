# AI Security Capability Monitor (AISCM)

Real-time tracker that monitors AI offensive security capabilities as they emerge. Tracks when AI models cross capability thresholds in exploit writing, vulnerability discovery, social engineering automation, malware generation, and network reconnaissance.

## Capability Matrix

| Category | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| **Exploit Writing** | Conceptual | Template | Functional | Adaptive | Novel (0-day) |
| **Vuln Discovery** | Pattern Match | Static Analysis | Deep Analysis | Cross-Component | Zero-Day Discovery |
| **Social Engineering** | Generic | Contextual | Personalized | Multi-Channel | Autonomous |
| **Malware Generation** | Conceptual | Scaffolding | Functional | Evasive | Polymorphic |
| **Network Recon** | Tool Usage | Guided Recon | Autonomous Scanning | Stealth Recon | Full Mapping |

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Evaluate a model
aiscm evaluate --model gpt-4o --category exploit-writing

# Launch dashboard
aiscm dashboard

# Track research papers
aiscm track-research

# View taxonomy
aiscm taxonomy

# View alerts
aiscm alerts
```

## Architecture

```
aiscm/
├── cli.py          # Click CLI interface
├── config.py       # YAML config loader
├── db.py           # SQLite storage layer
├── evaluator.py    # Benchmark runner + model API calls
├── research.py     # arXiv paper tracker
├── taxonomy.py     # Tier/category utilities
└── dashboard.py    # FastAPI web dashboard

config/
├── taxonomy.yaml   # L1-L5 capability definitions
├── benchmarks.yaml # Evaluation prompts + grading
└── models.yaml     # Model configurations
```

## How It Works

1. **Define capabilities** in `config/taxonomy.yaml` — 5 categories × 5 tiers (L1-L5)
2. **Run benchmarks** against model APIs — automated prompts with keyword-based grading
3. **Track tier changes** — alerts when a model crosses a capability threshold
4. **Monitor research** — arXiv scraping for emerging AI security papers
5. **Visualize** on the web dashboard — capability matrix, alerts, research feed

## Configuration

### API Keys

```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

Without API keys, evaluations run in simulated mode (scores based on expected benchmark tiers).

### Alert Webhook

Set `alerts.webhook_url` in `config/models.yaml` for Slack/Discord notifications.

## Docker

```bash
docker build -t aiscm .
docker run -p 8150:8150 aiscm
```

## Testing

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
