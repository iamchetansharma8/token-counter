import functools
import inspect
import time
from datetime import datetime

# from typing import Callable
import anthropic
import tiktoken

from logging_config import log
from models import CostEstimate, TokenCount, TokenCountResult

"""counter.py — the engine (all the real work)
A TokenCounter class with these responsibilities:

read_file(path) → returns the file's text (opens it with a with block; clear error if missing).
count_with_tiktoken(text) → token count via the local tiktoken library.
count_with_anthropic_api(text, model) → token count via Anthropic's count_tokens API (async).
estimate_cost(count, model) → tokens * price-per-token; returns 0.0 and warns for an unknown model.
process_file(path) → orchestrates all of the above and returns a TokenCountResult."""

# Pricing constants (as of May 2026 — update if needed)
# Pricing constants (as of May 2026 — update if needed)
MODEL_PRICING = {
    "claude-opus-4-8": {"input": 5, "output": 25},
    "claude-opus-4-7": {"input": 5, "output": 25},  # USD per MTok
    "claude-opus-4-6": {"input": 5, "output": 25},
    "claude-opus-4-5": {"input": 5, "output": 25},
    "claude-sonnet-4-6": {"input": 3, "output": 15},
    "claude-haiku-4-5": {"input": 1, "output": 5},
    "gpt-4o": {"input": 2.5, "output": 10},
    "o4-mini": {"input": 1.10, "output": 4.4},
    "gpt-5.2": {"input": 1.75, "output": 14},
    "gpt-5.2-pro": {"input": 21.00, "output": 168.00},
    "gpt-5.1": {"input": 1.25, "output": 10},
    "gpt-5-mini": {"input": 0.25, "output": 2},
    "gpt-5": {"input": 2.5, "output": 10},
    "llama-3": {"input": 0.5, "output": 1.5},
}

def universal_timer(decorated_func):
    if inspect.iscoroutinefunction(decorated_func):
        @functools.wraps(decorated_func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            res = await decorated_func(*args, **kwargs)
            elapsed_time = time.perf_counter() - start_time
            # print(f'Function call {decorated_func.__name__} took {elapsed_time:.6f}s to execute')
            log.info(f"{decorated_func.__name__} completed", duration_seconds=elapsed_time)
            return res
        return wrapper
    else:
        @functools.wraps(decorated_func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            res = decorated_func(*args, **kwargs)
            elapsed_time = time.perf_counter() - start_time
            # print(f'Function call {decorated_func.__name__} took {elapsed_time:.6f}s to execute')
            log.info(f"{decorated_func.__name__} completed", duration_seconds=elapsed_time)
            return res
        return wrapper


class TokenCounter:
    def __init__(self):
        self.client = anthropic.Anthropic()  # Requires ANTHROPIC_API_KEY env var
        self.log = log

    @universal_timer
    def read_file(self, path: str) -> str:
        try:
            with open(path, encoding='utf-8') as f:
                self.log.info('File opened, preparing to read', file_path=path)
                return f.read()
        except FileNotFoundError:
            self.log.error("file not found", file_path=path)
            raise
            # print('Raised FileNotFoundError')
        except Exception:
            self.log.exception("Exception raised while reading file", file_path=path)
            raise
            # print(f'Raised exception {e}')

    @universal_timer
    def count_with_tiktoken(self, text: str, model: str) -> int:
        encoding = tiktoken.encoding_for_model(model)
        num_of_tokens = encoding.encode(text)
        self.log.info("tiktoken count", tokens=num_of_tokens, encoding_model=model)
        return len(num_of_tokens)

    @universal_timer
    async def count_with_anthropic_api(self, text: str, model: str) -> int:
        try:
            client = anthropic.AsyncAnthropic()
            resp = await client.messages.count_tokens(
                model=model,
                messages=[{"role": "user", "content": text}],
                )
            tokens = resp.input_tokens
            self.log.info("anthropic api count", tokens=tokens, encoding_model=model)
            return tokens
        except TypeError as e:
            self.log.warning(
                "Anthropic authentication unavailable, skipping API count",
                encoding_model=model,
                error=str(e),
            )
            return 0
        except Exception as e:
            self.log.exception("Exception raised", encoding_model=model, error=e)
            raise

    @universal_timer
    def estimate_cost(self, count: int, model: str, is_output: bool = False) -> float:
        if model not in MODEL_PRICING:
            print(f'{model} pricing info not available')
            return 0.0
        cost_usd = MODEL_PRICING[model]["output"]
        if is_output:
            estimated_cost = (count*cost_usd)/1000000.0
        else:
            cost_usd = MODEL_PRICING[model]["input"]
            estimated_cost = (count*cost_usd)/1000000.0
        self.log.info("Estimated Cost Calculated", estimated_cost=estimated_cost, model=model, tokens=count, cost_usd=cost_usd)
        return estimated_cost

# process_file(path) → orchestrates all of the above and returns a TokenCountResult.
    @universal_timer
    async def process_file(self, path: str) -> TokenCountResult:
        """Main workflow: read file, count tokens, estimate costs."""
        text = self.read_file(path)
        file_size = len(text.encode())
        num_of_tokens_anthropic_api = await self.count_with_anthropic_api(text, 'claude-haiku-4-5')
        num_of_tokens_tiktoken_local = self.count_with_tiktoken(text, 'gpt-5-mini')
        estimated_raw_cost_claude_haiku_4_5 = self.estimate_cost(num_of_tokens_anthropic_api, 'claude-haiku-4-5')
        estimated_raw_cost_gpt_5_mini = self.estimate_cost(num_of_tokens_tiktoken_local, 'gpt-5-mini')
        estimated_cost_claude_haiku_4_5 = CostEstimate(model='claude-haiku-4-5',
                                                       token_count=num_of_tokens_anthropic_api,
                                                       cost_usd=estimated_raw_cost_claude_haiku_4_5)
        estimated_cost_gpt_5_mini = CostEstimate(model='gpt-5-mini',
                                                 token_count=num_of_tokens_tiktoken_local,
                                                 cost_usd=estimated_raw_cost_gpt_5_mini)
        token_count_claude_api = TokenCount(model='claude-haiku-4-5',
                                            tokenizer='claude_api_tokeniser',
                                            count=num_of_tokens_anthropic_api)
        token_count_tiktoken_local = TokenCount(model='gpt-5-mini',
                                                tokenizer='tiktoken_local_tokeniser',
                                                count=num_of_tokens_tiktoken_local)
        token_counts = [token_count_claude_api, token_count_tiktoken_local]
        cost_estimates = [estimated_cost_claude_haiku_4_5, estimated_cost_gpt_5_mini]
        token_count_result = TokenCountResult(file_path=path,
                                              file_size_bytes=str(file_size),
                                              token_counts=token_counts,
                                              cost_estimates=cost_estimates,
                                              timestamp=datetime.now())
        self.log.info("processing complete", file_path=path)
        return token_count_result



