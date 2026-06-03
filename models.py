from datetime import datetime

from pydantic import BaseModel, Field


# one tokenizer's result
class TokenCount(BaseModel):
    model: str
    tokenizer: str
    count: int = Field(ge=0)

# a model's cost:
class CostEstimate(BaseModel):
    model: str
    token_count: int = Field(ge=0)
    cost_usd: float = Field(ge=0)
    pricing_note: str | None = None

# the whole output that gets printed file path, file size, a list of TokenCounts, a list of CostEstimates, and a timestamp.
class TokenCountResult(BaseModel):
    file_path: str
    file_size_bytes: str
    token_counts: list[TokenCount]
    cost_estimates: list[CostEstimate]
    timestamp: datetime

# token_count_1 = TokenCount(model = 'OpenAI-o5', tokenizer = 'tiktoken', count = 10)
# token_count_2 = TokenCount(model = 'opus-4.8', tokenizer = 'Anthropic-Tokeniser', count = 15)
# token_counts = [token_count_1, token_count_2]
# cost_estimate_1 = CostEstimate(model = 'opus-4.8', token_count = 1000000, cost_usd = 5)
# cost_estimate_2 = CostEstimate(model = 'OpenAI-o5', token_count = 1500000, cost_usd = 4)
# cost_estimates = [cost_estimate_1, cost_estimate_2]
# print(f'token_count1: {token_count_1.model_dump_json(indent = 2)}')
# print(f'cost_estimate1: {cost_estimate_1.model_dump_json(indent = 2)}')
# token_count_result = TokenCountResult(file_path = '/Files/test_file.txt', file_size_bytes = '10KB', token_counts = token_counts, cost_estimates = cost_estimates, timestamp = datetime.now())
# print(f'token_count_result: {token_count_result.model_dump_json(indent = 2)}')
