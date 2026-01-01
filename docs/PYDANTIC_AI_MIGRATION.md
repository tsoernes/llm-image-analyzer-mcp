# PydanticAI Migration Guide

This document explains the migration from direct Azure OpenAI client to PydanticAI for model-agnostic support.

## What Changed

### Before: Direct Azure OpenAI

Previously, the server used the `openai` Python SDK directly, limiting it to Azure OpenAI models only:

```python
from openai import AsyncAzureOpenAI

client = AsyncAzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_API_VERSION,
)

response = await client.chat.completions.create(
    model=model_name,
    messages=[{"role": "user", "content": message_content}],
    max_tokens=max_tokens
)
```

### After: PydanticAI

Now, the server uses PydanticAI's model-agnostic interface, supporting multiple providers:

```python
from pydantic_ai import Agent, ImageUrl, BinaryContent, ModelSettings

agent = Agent(
    model="azure:gpt-5.2",  # or "openai:gpt-4o", "anthropic:claude-sonnet-4"
    model_settings=ModelSettings(max_tokens=1000)
)

result = await agent.run([prompt, image1, image2])
```

## Key Benefits

### 1. Model Agnostic
Switch between providers without changing code:
- **Azure OpenAI**: `azure:gpt-5.2`, `azure:gpt-4o`
- **OpenAI**: `openai:gpt-4o`, `openai:gpt-4-turbo`
- **Anthropic**: `anthropic:claude-sonnet-4`, `anthropic:claude-opus-4`
- **Google**: `google:gemini-2.0-flash-exp`
- **Groq**: `groq:llama-3.2-90b-vision-preview`
- And more!

### 2. Simplified Image Handling
PydanticAI provides clean abstractions:
- **URLs**: `ImageUrl(url="https://...")`
- **Local files**: `BinaryContent(data=bytes, media_type="image/jpeg")`

No manual base64 encoding needed - PydanticAI handles it.

### 3. Type Safety
PydanticAI leverages Pydantic for type-safe configuration and responses.

### 4. Consistent API
Same interface across all providers - no provider-specific quirks to handle.

## Breaking Changes

### Environment Variables

**Old:**
```bash
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_API_KEY=xxx
AZURE_OPENAI_MODEL=gpt-5.2
```

**New:**
```bash
MODEL=azure:gpt-5.2  # Provider prefix required

# Azure config (only if using azure: models)
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_API_KEY=xxx

# OpenAI config (only if using openai: models)
OPENAI_API_KEY=xxx

# Anthropic config (only if using anthropic: models)
ANTHROPIC_API_KEY=xxx
```

### Model Parameter Format

**Old:**
```json
{
  "model": "gpt-5.2"  // Just the model name
}
```

**New:**
```json
{
  "model": "azure:gpt-5.2"  // Provider prefix required
}
```

### Response Format

**Old:**
```json
{
  "analysis": "...",
  "model": "gpt-5.2",
  "prompt_tokens": 100,
  "completion_tokens": 50,
  "total_tokens": 150
}
```

**New:**
```json
{
  "analysis": "...",
  "model": "azure:gpt-5.2",
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "total_tokens": 150
  }
}
```

Token counts are now nested under `usage` object (may be absent if provider doesn't report usage).

### Detail Parameter Removed

**Old:**
```json
{
  "prompt": "Describe this image",
  "image_paths": ["image.jpg"],
  "detail": "high"  // This parameter existed
}
```

**New:**
```json
{
  "prompt": "Describe this image",
  "image_paths": "image.jpg"  // Can now be single string!
  // detail parameter removed - PydanticAI handles encoding automatically
}
```

The `detail` parameter was OpenAI-specific and controlled image resolution (low/high). PydanticAI abstracts this away and handles image encoding automatically. If you need to control image quality, resize images before sending them.

## Migration Steps

### For Users

1. **Update `.env` file:**
   ```bash
   # Add MODEL variable with provider prefix
   MODEL=azure:gpt-5.2
   
   # Remove old AZURE_OPENAI_MODEL variable
   # AZURE_OPENAI_MODEL=gpt-5.2  # DELETE THIS
   ```

2. **Update model parameter in tool calls:**
   - Change `"model": "gpt-4o"` → `"model": "azure:gpt-4o"`
   - Or switch providers: `"model": "openai:gpt-4o"`

3. **Update tool calls:**
   - Remove `detail` parameter if present
   - `image_paths` can now be a single string (not just array)
   
4. **Update response parsing (if needed):**
   - Change `result["prompt_tokens"]` → `result["usage"]["prompt_tokens"]`
   - Handle case where `usage` might be absent

### For Developers

1. **Pull latest code:**
   ```bash
   git pull origin master
   ```

2. **Update dependencies:**
   ```bash
   uv sync
   ```

3. **Test with new format:**
   ```bash
   uv run llm-image-analyzer-mcp
   ```

## GPT-5 Models: max_completion_tokens

GPT-5 models use `max_completion_tokens` instead of `max_tokens`. The server automatically detects GPT-5 models and converts the parameter:

```python
# You specify (for any model including GPT-5):
{
  "model": "azure:gpt-5.2",
  "max_tokens": 1000
}

# Server converts for GPT-5:
ModelSettings(max_completion_tokens=1000)  # For GPT-5

# Or for other models:
ModelSettings(max_tokens=1000)  # For GPT-4, Claude, etc.
```

No action needed - this is handled automatically.

## Provider-Specific Notes

### Azure OpenAI

Requires environment variables:
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

Model format: `azure:gpt-5.2`, `azure:gpt-4o`

### OpenAI

Requires environment variable:
```bash
OPENAI_API_KEY=sk-...
```

Model format: `openai:gpt-4o`, `openai:gpt-4-turbo`

### Anthropic

Requires environment variable:
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

Model format: `anthropic:claude-sonnet-4`, `anthropic:claude-opus-4`

Note: Claude models have excellent vision capabilities!

### Other Providers

See [PydanticAI documentation](https://ai.pydantic.dev/models/) for full list of supported providers.

## Troubleshooting

### "Azure OpenAI not configured" error

**Cause:** Using `azure:` model without required environment variables.

**Solution:** Either:
1. Set `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY`, OR
2. Switch to another provider:
   ```bash
   MODEL=openai:gpt-4o
   OPENAI_API_KEY=sk-...
   ```

### "Model not found" error

**Cause:** Missing provider prefix in model name.

**Solution:** Add provider prefix:
- ❌ `"model": "gpt-4o"`
- ✅ `"model": "azure:gpt-4o"` or `"model": "openai:gpt-4o"`

### Missing token usage in response

**Cause:** Some providers don't report token usage.

**Solution:** This is normal. Check if `usage` key exists before accessing:
```python
if "usage" in result:
    total = result["usage"]["total_tokens"]
```

## Rollback (if needed)

If you need to rollback to the direct Azure OpenAI version:

```bash
git checkout <commit-before-pydantic-ai>
uv sync
```

Then restore your old `.env` format.

## Testing Different Providers

### Azure OpenAI
```json
{
  "prompt": "Describe this image",
  "image_paths": "test.jpg",  // Single string now supported!
  "model": "azure:gpt-5.2"
}
```

### OpenAI
```json
{
  "prompt": "Describe this image",
  "image_paths": ["test1.jpg", "test2.jpg"],  // Array still works
  "model": "openai:gpt-4o"
}
```

### Anthropic Claude
```json
{
  "prompt": "Describe this image",
  "image_paths": "test.jpg",
  "model": "anthropic:claude-sonnet-4"
}
```

## Performance Comparison

All providers use the same efficient PydanticAI interface with:
- Async I/O throughout
- Automatic retry logic
- Connection pooling
- Minimal overhead

Performance is primarily determined by the model and provider, not the client library.

## Future Enhancements

With PydanticAI, we can easily add:
- **Model fallbacks**: Try multiple models automatically
- **Response validation**: Enforce structured output schemas
- **Streaming responses**: Real-time token streaming
- **Cost tracking**: Track spend across providers
- **A/B testing**: Compare model performance

## Questions?

- **PydanticAI Docs**: https://ai.pydantic.dev/
- **Supported Models**: https://ai.pydantic.dev/models/
- **GitHub Issues**: https://github.com/tsoernes/llm-image-analyzer-mcp/issues