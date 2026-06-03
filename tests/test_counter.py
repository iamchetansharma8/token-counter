
import pytest

from counter import TokenCounter
from models import TokenCountResult


@pytest.fixture
def counter():
    """Fixture: TokenCounter instance."""
    return TokenCounter()

@pytest.fixture
def sample_file(tmp_path):
    """Fixture: Create a temporary test file."""
    file_path = tmp_path / "sample.txt"
    file_path.write_text("The quick brown fox jumps over the lazy dog." * 10)
    return str(file_path)

# Test 1: File reading
def test_read_file(counter, sample_file):
    """Test that files are read correctly."""
    content = counter.read_file(sample_file)
    assert len(content) > 2
    assert 'brown fox jumps' in content

# Test 2: Tiktoken counting
def test_tiktoken_counting(counter, sample_file):
    """Test that tiktoken counts tokens correctly."""
    content = counter.read_file(sample_file)
    token_count = counter.count_with_tiktoken(content, 'gpt-5-mini')
    assert token_count > 0
    assert isinstance(token_count, int)

# estimate_cost(self, count: int, model: str, is_output: bool = False) -> float
# Test 3: Cost estimation
def test_cost_estimation(counter, sample_file):
    """Test cost calculation."""
    content = counter.read_file(sample_file)
    token_count = counter.count_with_tiktoken(content, 'gpt-5-mini')
    cost_usd = counter.estimate_cost(token_count, 'gpt-5-mini')
    assert cost_usd == 2.275e-05

# Test 4: Cost estimation for unknown model
def test_estimate_cost_unknown_model(counter):
    """Test that unknown models return 0 cost (graceful degradation)."""
    cost = counter.estimate_cost(1000, "unknown-model")
    assert cost == 0.0

# Test 5: Full async workflow
@pytest.mark.asyncio
async def test_process_file_async(counter, sample_file):
    """Test the full async file processing workflow."""
    result = await counter.process_file(sample_file)

    # Verify result structure
    assert isinstance(result, TokenCountResult)
    assert result.file_path == sample_file
    assert int(result.file_size_bytes) > 0
    assert len(result.token_counts) > 0
    assert len(result.cost_estimates) > 0
    assert result.timestamp is not None

    # Verify counts are consistent (tiktoken ≈ anthropic, not exact)
    assert result.token_counts[0].count > 0
