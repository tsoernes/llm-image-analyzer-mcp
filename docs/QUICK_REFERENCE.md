# Quick Reference Card

## Installation

```bash
git clone https://github.com/tsoernes/llm-image-analyzer-mcp.git
cd llm-image-analyzer-mcp
uv sync
cp .env.example .env
# Edit .env with your Azure credentials
```

## Environment Variables

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_MODEL=gpt-5.2
MCP_DEBUG=false
```

## Tool: analyze_images

### Basic Syntax

```json
{
  "prompt": "Your question or instruction",
  "image_paths": "path/to/image.jpg",
  "model": "azure:gpt-5.2",
  "max_tokens": null,
  "reasoning_effort": "high"
}
```

### Parameters

| Parameter | Type | Required | Default | Options |
|-----------|------|----------|---------|---------|
| `prompt` | string | ✅ | - | Any instruction |
| `image_paths` | string or array | ✅ | - | Local paths or URLs (single or multiple) |
| `model` | string | ❌ | `azure:gpt-5.2` | Format: `provider:model-name` |
| `max_tokens` | int | ❌ | `null` | Any positive int (auto-converts for GPT-5) |
| `reasoning_effort` | string | ❌ | `"high"` | `"low"`, `"medium"`, `"high"` |

### Response

```json
{
  "analysis": "The model's response text...",
  "model": "azure:gpt-5.2",
  "usage": {
    "prompt_tokens": 1250,
    "completion_tokens": 450,
    "total_tokens": 1700
  }
}
```

Note: `usage` object may be absent if provider doesn't report token usage.

## Common Use Cases

### Compare Images
```json
{
  "prompt": "What changed between these screenshots?",
  "image_paths": ["before.png", "after.png"]
}
```

### Describe Image
```json
{
  "prompt": "Describe this image in detail",
  "image_paths": ["https://example.com/photo.jpg"],
  "detail": "high"
}
```

### Extract Text (OCR)
```json
{
  "prompt": "Extract all visible text",
  "image_paths": ["~/document.png"],
  "max_tokens": 1000
}
```

### Quick Analysis
```json
{
  "prompt": "Is this professional quality?",
  "image_paths": ["photo.jpg"],
  "detail": "low",
  "reasoning_effort": "low"
}
```

## Model Providers

| Provider | Format | Example | Notes |
|----------|--------|---------|-------|
| Azure OpenAI | `azure:model` | `azure:gpt-5.2` | Requires Azure credentials |
| OpenAI | `openai:model` | `openai:gpt-4o` | Requires OpenAI API key |
| Anthropic | `anthropic:model` | `anthropic:claude-sonnet-4` | Excellent vision support |
| See [PydanticAI docs](https://ai.pydantic.dev/models/) for more | | |

## Reasoning Effort

| Level | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| `"low"` | ⚡⚡⚡ Fast | ⭐ Basic | Quick checks |
| `"medium"` | ⚡⚡ Moderate | ⭐⭐ Good | Balanced |
| `"high"` | ⚡ Slower | ⭐⭐⭐ Best | Detailed analysis |

## Image Path Formats

| Format | Example | Notes |
|--------|---------|-------|
| Single string | `"image.jpg"` | **New!** Can pass single image as string |
| Array | `["img1.jpg", "img2.jpg"]` | Multiple images |
| Absolute | `/home/user/image.jpg` | Full path |
| Home | `~/photos/pic.png` | Expands `~` |
| URL | `https://example.com/img.jpg` | HTTP/HTTPS only |

## Supported Formats

✅ JPEG (`.jpg`, `.jpeg`)  
✅ PNG (`.png`)  
✅ GIF (`.gif`)  
✅ WebP (`.webp`)

## Error Handling

### File Not Found
```json
{
  "error": "Image not found at path: X. Please check that the file exists...",
  "error_type": "FileNotFoundError"
}
```

### Invalid Format
```json
{
  "error": "Invalid image file at X. Supported formats: JPEG, PNG, GIF, WebP",
  "error_type": "ValueError"
}
```

### Missing Config
```json
{
  "error": "Azure OpenAI not configured. Please set AZURE_OPENAI_ENDPOINT...",
  "error_type": "ConfigurationError"
}
```

## Debug Mode

Enable detailed errors:
```bash
export MCP_DEBUG=true
```

Error response includes:
```json
{
  "error": "Error message",
  "error_type": "ExceptionType",
  "traceback": "Full stack trace...",
  "debug_mode": true
}
```

## Running the Server

### Stdio (MCP Standard)
```bash
uv run llm-image-analyzer-mcp
```

### Development Mode
```bash
uv run python -m llm_image_analyzer_mcp.server
```

### Testing with Inspector
```bash
npx @modelcontextprotocol/inspector uv run llm-image-analyzer-mcp
```

## Claude Desktop Config

**File:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "llm-image-analyzer": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/llm-image-analyzer-mcp",
        "run",
        "llm-image-analyzer-mcp"
      ],
      "env": {
        "MODEL": "azure:gpt-5.2",
        "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Performance Tips

1. **Single string for one image** - simpler syntax: `"image.jpg"` vs `["image.jpg"]`
2. **Set `max_tokens`** for concise answers → saves cost (auto-converts for GPT-5)
3. **Use URLs** when possible → avoids local file encoding
4. **Batch images** in one call → reduces overhead
5. **Use `reasoning_effort="low"`** for quick tasks → faster
6. **Try different providers** - compare speed/quality/cost

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Server not found | Check absolute path in config |
| Azure error | Verify `.env` credentials |
| Image not found | Use absolute paths or URLs |
| Timeout | Try `detail="low"` or fewer images |
| Rate limit | Reduce concurrent requests |

## Links

- **GitHub:** https://github.com/tsoernes/llm-image-analyzer-mcp
- **Issues:** https://github.com/tsoernes/llm-image-analyzer-mcp/issues
- **Setup Guide:** [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md)
- **Examples:** [../examples/example_usage.md](../examples/example_usage.md)