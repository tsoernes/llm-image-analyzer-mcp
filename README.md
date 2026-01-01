# LLM Image Analyzer MCP Server

FastMCP server for analyzing images using Azure OpenAI vision models (GPT-4o, GPT-5.2, etc.).

## Features

- 🖼️ **Analyze images** with custom prompts using Azure OpenAI vision models
- 📁 **Support for local files and URLs** - works with both local image paths and web URLs
- 🎨 **Multiple image formats** - JPEG, PNG, GIF, WebP
- 🔧 **Flexible configuration** - customize model, tokens, detail level, reasoning effort
- 🐛 **Debug mode** - full stack traces when `MCP_DEBUG=true`
- ⚡ **Async I/O** - efficient async operations throughout
- 📊 **Token usage tracking** - see prompt, completion, and total tokens used

## Use Cases

- Compare two or more images (e.g., screenshots, designs)
- Describe image content in detail
- Extract text from images (OCR)
- Identify objects, people, scenes, or brands
- Answer questions about visual content
- Analyze diagrams, charts, or infographics

## Installation

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager
- Azure OpenAI account with vision model deployment

### Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd llm-image-analyzer
```

2. **Install dependencies:**
```bash
uv sync
```

3. **Configure environment variables:**

Create a `.env` file in the project root:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_MODEL=gpt-5.2
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Optional: Enable debug mode for detailed error traces
MCP_DEBUG=false
```

**Required environment variables:**
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key

**Optional environment variables:**
- `AZURE_OPENAI_MODEL` - Default model (default: `gpt-5.2`)
- `AZURE_OPENAI_API_VERSION` - API version (default: `2024-12-01-preview`)
- `MCP_DEBUG` - Enable debug mode with full stack traces (default: `false`)

## Usage

### Running the Server

**Stdio transport (default for MCP):**
```bash
uv run llm-image-analyzer-mcp
```

**For development:**
```bash
uv run python -m llm_image_analyzer_mcp.server
```

### MCP Tool: `analyze_images`

Analyze one or more images using Azure OpenAI vision models.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | `str` | Yes | - | Question or instruction for analyzing the image(s) |
| `image_paths` | `list[str]` | Yes | - | List of local file paths or URLs to images |
| `model` | `str` | No | `gpt-5.2` | Azure OpenAI model deployment name |
| `max_tokens` | `int` | No | `None` | Maximum tokens in response (None = no limit) |
| `detail` | `str` | No | `"auto"` | Image detail level: `"auto"`, `"low"`, or `"high"` |
| `reasoning_effort` | `str` | No | `"high"` | Reasoning effort: `"low"`, `"medium"`, or `"high"` |

#### Response

Returns a dictionary with:
- `analysis` - The model's text response
- `model` - Model name used
- `prompt_tokens` - Tokens in prompt (if available)
- `completion_tokens` - Tokens in response (if available)
- `total_tokens` - Total tokens used (if available)

#### Examples

**Compare two screenshots:**
```json
{
  "prompt": "What are the differences between these two screenshots?",
  "image_paths": [
    "/home/user/screenshots/before.png",
    "/home/user/screenshots/after.png"
  ]
}
```

**Describe an image from URL:**
```json
{
  "prompt": "Describe this image in detail",
  "image_paths": ["https://example.com/photo.jpg"],
  "detail": "high"
}
```

**Extract text with custom model:**
```json
{
  "prompt": "Extract all visible text from this document",
  "image_paths": ["~/documents/scan.png"],
  "model": "gpt-4o",
  "max_tokens": 500
}
```

**Analyze diagram with low reasoning effort:**
```json
{
  "prompt": "What type of diagram is this and what does it show?",
  "image_paths": ["https://example.com/diagram.png"],
  "reasoning_effort": "low",
  "detail": "low"
}
```

## Configuration Options

### Image Detail Levels

The `detail` parameter controls image resolution sent to the API:

- **`"auto"`** (default) - Let the model decide based on image content
- **`"low"`** - 512x512 resolution, faster and cheaper, less detail
- **`"high"`** - 2048x2048 resolution, slower and more expensive, more detail

Use `"low"` for simple images or when speed/cost matters. Use `"high"` for complex images with fine details.

### Reasoning Effort

The `reasoning_effort` parameter controls model thoroughness:

- **`"low"`** - Faster responses, less thorough analysis
- **`"medium"`** - Balanced speed and quality
- **`"high"`** (default) - Most thorough analysis, best quality

### Model Selection

You can override the default model per request:

1. **Environment variable** (applies to all requests):
   ```bash
   AZURE_OPENAI_MODEL=gpt-4o
   ```

2. **Per-request parameter** (overrides env var):
   ```json
   {
     "model": "gpt-4o",
     "prompt": "...",
     "image_paths": [...]
   }
   ```

## Debug Mode

Enable debug mode for detailed error information:

```bash
export MCP_DEBUG=true
```

In debug mode:
- Full stack traces returned in error responses
- Detailed logging to console
- Image encoding details logged

**Production mode** (default):
- Compact error messages
- Minimal logging
- No internal details exposed

## Error Handling

The server provides actionable error messages:

- **Missing image file**: "Image not found at path: X. Please check that the file exists and the path is correct."
- **Invalid image format**: "Invalid image file at X. Supported formats: JPEG, PNG, GIF, WebP."
- **Inaccessible URL**: "Failed to access URL: X. Error: connection timeout"
- **Missing config**: "Azure OpenAI not configured. Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env file."

## Development

### Project Structure

```
llm-image-analyzer/
├── src/
│   └── llm_image_analyzer_mcp/
│       ├── __init__.py          # Package metadata
│       ├── server.py            # Main MCP server
│       └── py.typed             # Type hints marker
├── .env                         # Environment variables (not in git)
├── .env.example                 # Example environment file
├── .gitignore                   # Git ignore patterns
├── pyproject.toml               # Project metadata and dependencies
└── README.md                    # This file
```

### Running Tests

```bash
# Install dev dependencies
uv sync --dev

# Run tests (when available)
uv run pytest
```

### Code Quality

```bash
# Type checking
uv run mypy src/

# Linting
uv run ruff check src/

# Formatting
uv run ruff format src/
```

## Dependencies

- **fastmcp** - MCP server framework
- **openai** - Azure OpenAI client
- **python-dotenv** - Environment variable loading
- **pillow** - Image format validation
- **httpx** - Async HTTP client for URL validation

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review debug logs with `MCP_DEBUG=true`

## Changelog

### 0.1.0 (2026-01-01)

- Initial release
- `analyze_images` tool with multi-image support
- Support for local files and URLs
- Configurable model, tokens, detail, reasoning effort
- Debug mode with stack traces
- Comprehensive error handling