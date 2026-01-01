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
  "image_paths": ["path/to/image.jpg"],
  "model": "gpt-5.2",
  "max_tokens": null,
  "detail": "auto",
  "reasoning_effort": "high"
}
```

### Parameters

| Parameter | Type | Required | Default | Options |
|-----------|------|----------|---------|---------|
| `prompt` | string | ✅ | - | Any instruction |
| `image_paths` | array | ✅ | - | Local paths or URLs |
| `model` | string | ❌ | `gpt-5.2` | Any Azure deployment |
| `max_tokens` | int | ❌ | `null` | Any positive int |
| `detail` | string | ❌ | `"auto"` | `"auto"`, `"low"`, `"high"` |
| `reasoning_effort` | string | ❌ | `"high"` | `"low"`, `"medium"`, `"high"` |

### Response

```json
{
  "analysis": "The model's response text...",
  "model": "gpt-5.2",
  "prompt_tokens": 1250,
  "completion_tokens": 450,
  "total_tokens": 1700
}
```

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

## Detail Levels

| Level | Resolution | Use Case | Cost |
|-------|-----------|----------|------|
| `"low"` | 512x512 | Simple images, speed | 💰 Low |
| `"auto"` | Dynamic | General use | 💰💰 Medium |
| `"high"` | 2048x2048 | Fine details | 💰💰💰 High |

## Reasoning Effort

| Level | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| `"low"` | ⚡⚡⚡ Fast | ⭐ Basic | Quick checks |
| `"medium"` | ⚡⚡ Moderate | ⭐⭐ Good | Balanced |
| `"high"` | ⚡ Slower | ⭐⭐⭐ Best | Detailed analysis |

## Image Path Formats

| Format | Example | Notes |
|--------|---------|-------|
| Absolute | `/home/user/image.jpg` | Full path |
| Home | `~/photos/pic.png` | Expands `~` |
| Relative | `./images/photo.jpg` | From current dir |
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
        "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Performance Tips

1. **Use `detail="low"`** for simple images → 3-5x faster
2. **Set `max_tokens`** for concise answers → saves cost
3. **Use URLs** when possible → avoids encoding
4. **Batch images** in one call → reduces overhead
5. **Use `reasoning_effort="low"`** for quick tasks → faster

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