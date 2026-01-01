# Changelog

All notable changes to the LLM Image Analyzer MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

- **0.2.0** (2026-01-01): PydanticAI integration, multi-provider support
- **0.1.0** (2026-01-01): Initial release with Azure OpenAI