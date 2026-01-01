# Tests

This directory contains tests for the LLM Image Analyzer MCP Server.

## Test Files

### Unit Tests

- **`test_tool_signature.py`** - Unit tests for tool signature and parameter validation
  - Tests parameter validation without requiring API credentials
  - Validates that single string and array formats work for `image_paths`
  - Tests error response format
  - Run with: `uv run pytest tests/test_tool_signature.py -v`

### Integration Tests

- **`test_analyze_swan.py`** - Integration test with real image analysis
  - Tests analyzing a swan image from URL
  - Validates that the model correctly identifies the bird
  - Requires valid API credentials in `.env` file
  - Run with: `uv run python tests/test_analyze_swan.py`

## Running Tests

### Setup

1. **Install test dependencies:**
   ```bash
   uv sync --dev
   ```

2. **Configure environment variables** (for integration tests):
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

### Unit Tests (No Credentials Required)

Run unit tests that validate tool signature and parameter handling:

```bash
# Run all unit tests
uv run pytest tests/test_tool_signature.py -v

# Run specific test
uv run pytest tests/test_tool_signature.py::TestToolSignature::test_single_string_image_path_accepted -v
```

### Integration Tests (Requires Credentials)

Run integration tests that make actual API calls:

```bash
# Test with swan image
uv run python tests/test_analyze_swan.py
```

**Prerequisites:**
- Valid API credentials in `.env` file
- One of:
  - Azure OpenAI: `AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_API_KEY`
  - OpenAI: `OPENAI_API_KEY` + set `MODEL=openai:gpt-4o`
  - Anthropic: `ANTHROPIC_API_KEY` + set `MODEL=anthropic:claude-sonnet-4`

### Run All Tests

```bash
# Unit tests only (no credentials)
uv run pytest tests/test_tool_signature.py -v

# Integration tests (requires credentials)
uv run python tests/test_analyze_swan.py
```

## Test Coverage

### What's Tested

✅ **Parameter Validation:**
- Empty prompt detection
- Empty image_paths detection
- Invalid reasoning_effort values
- Single string vs array for image_paths

✅ **Response Format:**
- Tool returns dictionary
- Error responses have required fields
- Debug mode field present

✅ **Real Image Analysis (Integration):**
- URL image loading
- Swan identification in analysis
- Both string and array formats for image_paths

### What's NOT Tested Yet

⚠️ **Missing Tests:**
- Local file image loading
- Multiple images in one request
- Different model providers (OpenAI, Anthropic)
- Token usage reporting
- GPT-5 max_completion_tokens conversion
- Error handling for invalid URLs
- Error handling for unsupported image formats

## Writing New Tests

### Unit Test Template

```python
import pytest
from llm_image_analyzer_mcp.server import analyze_images

@pytest.mark.asyncio
async def test_my_feature():
    """Test description."""
    result = await analyze_images(
        prompt="Test prompt",
        image_paths="test.jpg"
    )
    
    assert isinstance(result, dict)
    # Add your assertions
```

### Integration Test Template

```python
import asyncio
from llm_image_analyzer_mcp.server import analyze_images

async def test_real_api_call():
    """Test with real API call."""
    result = await analyze_images(
        prompt="Describe this image",
        image_paths="https://example.com/image.jpg"
    )
    
    assert "analysis" in result
    assert "swan" in result["analysis"].lower()

if __name__ == "__main__":
    asyncio.run(test_real_api_call())
```

## CI/CD

Currently, tests are run manually. Future CI/CD integration could:

- Run unit tests on every commit
- Run integration tests on main branch only (with secrets)
- Generate coverage reports
- Enforce minimum test coverage

## Test Data

Test images should be:
- Publicly accessible URLs (for integration tests)
- Small file sizes (< 1MB preferred)
- Clear, recognizable subjects
- Properly licensed for testing

**Example Test Image:**
- Swan: https://imgs.search.brave.com/lihQwK1YQAyaVV5R3XeU-pxIX1bUthDslrElxE_GLbU/...

## Debugging Tests

### Enable Debug Mode

Set `MCP_DEBUG=true` in `.env` to get full stack traces:

```bash
MCP_DEBUG=true uv run python tests/test_analyze_swan.py
```

### Run Single Test

```bash
# Unit test
uv run pytest tests/test_tool_signature.py::TestToolSignature::test_single_string_image_path_accepted -v

# Integration test (modify the file to run only one test)
```

### Verbose Output

```bash
# Pytest verbose
uv run pytest tests/ -v -s

# Python script with prints
uv run python tests/test_analyze_swan.py
```

## Contributing Tests

When adding new features, please add tests:

1. **Add unit tests** for parameter validation
2. **Add integration tests** for real API behavior
3. **Update this README** with new test descriptions
4. **Ensure tests pass** before submitting PR

## Test Requirements

Tests require these dependencies:

- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `python-dotenv` - Environment variable loading
- `pydantic-ai` - For model interactions
- `httpx` - For HTTP requests

Install with: `uv sync --dev`
