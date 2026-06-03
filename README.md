# token-counter

A CLI tool that counts tokens in a file using two independent tokenizers and estimates the cost to process that file across multiple LLM models.

## What it does

Given a file path, it:

1. Reads the file
2. Counts tokens via the **Anthropic API** (`count_tokens` endpoint — exact tokenization for Claude models)
3. Counts tokens via **tiktoken** locally (OpenAI-compatible, no API call)
4. Estimates input cost in USD for each model based on current pricing

Results are logged as structured JSON to the console and `Files/production.log`.

## Setup

**Requirements:** Python 3.11+, [uv](https://docs.astral.sh/uv/)

```bash
# Install dependencies
uv sync

# Add your Anthropic API key
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

## Usage

```bash
uv run python cli.py path/to/your/file.txt
```

**Example output (structured JSON log):**
```json
{
  "file_path": "Files/test_file.txt",
  "file_size_bytes": "74",
  "token_counts": [
    {"model": "claude-haiku-4-5", "tokenizer": "claude_api_tokeniser", "count": 12},
    {"model": "gpt-5-mini", "tokenizer": "tiktoken_local_tokeniser", "count": 11}
  ],
  "cost_estimates": [
    {"model": "claude-haiku-4-5", "token_count": 12, "cost_usd": 1.2e-05},
    {"model": "gpt-5-mini", "token_count": 11, "cost_usd": 2.75e-06}
  ],
  "timestamp": "2026-06-03T10:00:00"
}
```

## Running tests

```bash
uv run pytest tests/ -v
```

## Project structure

```
token-counter/
├── counter.py        # TokenCounter class — core logic
├── models.py         # Pydantic models (TokenCount, CostEstimate, TokenCountResult)
├── cli.py            # CLI entry point
├── logging_config.py # Structured JSON logging via structlog
├── tests/
│   └── test_counter.py
├── Files/
│   └── test_file.txt # Sample input file
└── pyproject.toml
```

## Supported models and pricing

| Model | Input (per MTok) | Output (per MTok) |
|-------|-----------------|-------------------|
| claude-opus-4-8 | $5.00 | $25.00 |
| claude-sonnet-4-6 | $3.00 | $15.00 |
| claude-haiku-4-5 | $1.00 | $5.00 |
| gpt-5-mini | $0.25 | $2.00 |
| gpt-5 | $2.50 | $10.00 |
| o4-mini | $1.10 | $4.40 |

Pricing is defined in `counter.py` — update `MODEL_PRICING` as rates change.
