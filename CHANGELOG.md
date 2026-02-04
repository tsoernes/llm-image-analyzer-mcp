# Changelog

All notable changes to the LLM Image Analyzer MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Two-Step Path Resolution Fallback**: Improved path handling for relative paths
  - Automatically tries path relative to current working directory first
  - Falls back to stripping first directory component if initial attempt fails
  - Helps handle cases where users include project root directory in paths
  - Example: `myproject/images/photo.jpg` automatically resolves to `images/photo.jpg` if needed
  - Applies to all image path inputs across all tools
  - See `docs/PATH_RESOLUTION.md` for detailed documentation

## [0.4.0] - 2026-01-06

### Added
- **Mistral Document AI Support**: New `use_mistral` parameter for specialized document processing
  - Integration with Azure Mistral Document AI via Azure Foundry
  - Optimized for OCR, scanned documents, forms, invoices, and tables
  - Superior text extraction quality for complex document layouts
  - Native support for structured documents with tables
  - Uses same Azure endpoint and API key as Azure OpenAI
  - Configurable via `AZURE_MISTRAL_DEPLOYMENT` environment variable (default: `mistral-document-ai-2505`)
- **New dependency**: `mistralai-azure` (installed from GitHub)
- **SVG Support**: Automatic conversion of SVG files to PNG for processing
  - Uses `cairosvg` library for high-quality conversion
  - Works with both PydanticAI and Mistral Document AI
  - Transparent to users - just pass SVG paths like any other image
  - 150 DPI conversion for optimal text recognition
- **New dependency**: `cairosvg` for SVG conversion
- **Enhanced documentation**: Updated README with Mistral usage examples and configuration

### Changed
- Updated `pyproject.toml` to include `mistralai-azure` from git source
- Version bumped to 0.4.0

### Features
- **When to use Mistral**:
  - Scanned documents requiring high-quality OCR
  - Forms, invoices, receipts with structured layouts
  - Documents containing tables
  - Text extraction from complex layouts
  - High-accuracy document understanding tasks
- **Benefits**:
  - Superior OCR quality compared to general vision models
  - Excellent table detection and extraction
  - Native form and structured document support
  - Works with local files and URLs
  - Supports JPEG, PNG, GIF, WebP, SVG formats

### Limitations
- `output_schema` parameter is not supported when `use_mistral=True`
- Returns text analysis only (no structured output with Mistral)

### Examples
```json
{
  "prompt": "Extract all text and tables from this document",
  "image_paths": ["scanned_document.pdf"],
  "use_mistral": true
}
```

```json
{
  "prompt": "Extract invoice details including line items and totals",
  "image_paths": ["invoice.png"],
  "use_mistral": true
}
```

### Configuration
- Requires `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY`
- Optional: `AZURE_MISTRAL_DEPLOYMENT` (default: `mistral-document-ai-2505`)
- Updated `.env.example` with Mistral configuration

### SVG Support Details
- SVG files automatically detected by `.svg` extension
- Converted to PNG at 150 DPI for optimal quality
- Works seamlessly with both standard vision models and Mistral
- No user action required - just pass SVG paths
- Useful for technical drawings, diagrams, flowcharts, schematics

## [Unreleased - Future]

### Added
- **Relative Path Resolution**:
  - Relative paths (e.g., `"image.jpg"`, `"screenshots/before.png"`) are now resolved against the current working directory (`Path.cwd()`)
  - Enables natural path usage when MCP server is launched with `uv run --project`
  - Absolute paths, URLs, and `~` expansion work as before
  - Comprehensive test coverage with 7 unit tests

### Changed
- **Recommended Zed Configuration**: Use `--project` instead of `--directory` flag when launching the server
  - With `--project`, `Path.cwd()` returns the caller's directory (your workspace)
  - With `--directory`, `Path.cwd()` returns the switched-to directory (server's installation dir)
  - This makes relative paths resolve against your workspace automatically

### Benefits
- Simple and intuitive - relative paths work naturally from your workspace
- No extra parameters needed
- Works seamlessly with `uv run --project`
- Backwards compatible - absolute paths and URLs unaffected

## [0.3.0] - 2026-01-01

### Added
- **Structured Output Support**: New `output_schema` parameter for type-safe data extraction
  - Extract specific fields from images using JSON schemas
  - Perfect for receipts, invoices, forms, product details
  - Returns structured `data` instead of free-form text
  - Supports all JSON schema types: string, number, integer, boolean, array, object
  - Required and optional fields supported
  - Powered by PydanticAI's structured output capabilities
- **11 new unit tests** for structured output validation
  - Schema acceptance and validation
  - Multiple field types and combinations
  - Required vs optional fields
  - Backwards compatibility with text output

### Benefits
- Type-safe, predictable responses for programmatic use
- No parsing of free-form text needed
- Automatic validation against schema
- Ideal for data extraction workflows

### Examples
```json
{
  "prompt": "Extract receipt info",
  "image_paths": "receipt.jpg",
  "output_schema": {
    "type": "object",
    "properties": {
      "merchant": {"type": "string"},
      "total": {"type": "number"}
    }
  }
}
```

### Testing
- 11/11 new structured output tests passing
- 11/11 existing unit tests still passing
- Backwards compatible - no breaking changes

## [0.2.0] - 2026-01-01

### Added
- **PydanticAI Integration**: Model-agnostic support for multiple providers
  - Azure OpenAI (e.g., `azure:gpt-5.2`, `azure:gpt-4o`)
  - OpenAI (e.g., `openai:gpt-4o`, `openai:gpt-4-turbo`)
  - Anthropic (e.g., `anthropic:claude-sonnet-4`)
  - And more via [PydanticAI](https://ai.pydantic.dev/models/)
- **Simplified image_paths parameter**: Now accepts single string or array
  - Before: `"image_paths": ["image.jpg"]`
  - After: `"image_paths": "image.jpg"` or `["img1.jpg", "img2.jpg"]`
- **Automatic GPT-5 handling**: Auto-converts `max_tokens` to `max_completion_tokens` for GPT-5 models
- **Comprehensive documentation**:
  - PydanticAI migration guide (`docs/PYDANTIC_AI_MIGRATION.md`)
  - Zed Editor setup guide (`docs/ZED_SETUP.md`)
  - Updated Quick Reference with new parameters
- **Zed Editor integration**: Automatically added to `~/.config/zed/settings.json`

### Changed
- **BREAKING**: Model parameter now requires provider prefix
  - Old: `"model": "gpt-5.2"`
  - New: `"model": "azure:gpt-5.2"`
- **BREAKING**: Response format changed
  - Token counts now nested under `usage` object
  - Old: `{"prompt_tokens": 100, "completion_tokens": 50}`
  - New: `{"usage": {"prompt_tokens": 100, "completion_tokens": 50}}`
- **BREAKING**: Environment variable `AZURE_OPENAI_MODEL` renamed to `MODEL`
  - Old: `AZURE_OPENAI_MODEL=gpt-5.2`
  - New: `MODEL=azure:gpt-5.2`
- Replaced `openai` SDK with `pydantic-ai` for model-agnostic support
- Updated `.env.example` with provider-specific configurations
- Improved error messages to suggest alternative providers

### Removed
- **BREAKING**: `detail` parameter removed from `analyze_images` tool
  - Reason: Not supported by PydanticAI's abstraction layer
  - PydanticAI handles image encoding automatically
  - If image quality control is needed, resize images before sending

### Fixed
- GPT-5 models now correctly use `max_completion_tokens` instead of `max_tokens`
- Environment variable validation now only checks Azure config when using Azure models

### Migration Guide
See `docs/PYDANTIC_AI_MIGRATION.md` for detailed migration instructions.

**Quick Migration:**
1. Update `.env`: Change `AZURE_OPENAI_MODEL=gpt-5.2` to `MODEL=azure:gpt-5.2`
2. Update tool calls: Add provider prefix to model parameter
3. Update response parsing: Access tokens via `result["usage"]["prompt_tokens"]`
4. Remove `detail` parameter if present
5. Optionally simplify single-image calls: `"image.jpg"` instead of `["image.jpg"]`

## [0.1.0] - 2026-01-01

### Added
- Initial release with direct Azure OpenAI integration
- `analyze_images` tool with multi-image support
- Support for local file paths and URLs
- Image format validation (JPEG, PNG, GIF, WebP)
- Configurable parameters:
  - `model`: Azure OpenAI model deployment name
  - `max_tokens`: Response length control
  - `detail`: Image quality level (auto/low/high)
  - `reasoning_effort`: Model thoroughness (low/medium/high)
- Debug mode with full stack traces (`MCP_DEBUG=true`)
- Async I/O throughout for efficient operations
- Token usage tracking (prompt/completion/total)
- Comprehensive error handling with actionable messages
- Documentation:
  - Complete README with examples
  - MCP client setup guide (Claude Desktop, Cline)
  - Quick reference card
  - Example usage patterns
- FastMCP server framework
- Stdio transport (MCP standard)
- MIT License

### Security
- Environment variable validation on startup
- Sensitive credentials in `.env` file (gitignored)
- Path traversal prevention for local images
- Image format validation before processing

---

## Upgrading

### From 0.1.0 to 0.2.0

**Required Actions:**
1. Update dependencies: `uv sync`
2. Update `.env` file format (see migration guide)
3. Update model parameters with provider prefixes
4. Update response parsing for nested `usage` object
5. Remove `detail` parameter from tool calls

**Optional Actions:**
- Switch to different providers (OpenAI, Anthropic)
- Simplify single-image calls to use string instead of array
- Add Zed Editor integration

See `docs/PYDANTIC_AI_MIGRATION.md` for complete upgrade instructions.

---

## Links

- **Repository**: https://github.com/tsoernes/llm-image-analyzer-mcp
- **Issues**: https://github.com/tsoernes/llm-image-analyzer-mcp/issues
- **PydanticAI**: https://ai.pydantic.dev/
- **FastMCP**: https://gofastmcp.com/

---

## Version History

- **Unreleased**: Relative path resolution using Path.cwd()
- **0.4.0** (2026-01-06): Mistral Document AI support + SVG file support
- **0.3.0** (2026-01-01): Structured output support with JSON schemas
- **0.2.0** (2026-01-01): PydanticAI integration, multi-provider support
- **0.1.0** (2026-01-01): Initial release with Azure OpenAI