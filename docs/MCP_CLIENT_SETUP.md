# MCP Client Setup Guide

This guide shows how to configure the LLM Image Analyzer MCP Server with various MCP clients.

## Prerequisites

1. **Clone and setup the server:**
```bash
git clone https://github.com/tsoernes/llm-image-analyzer-mcp.git
cd llm-image-analyzer-mcp
uv sync
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

## Claude Desktop

### Configuration

Edit your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux:** `~/.config/Claude/claude_desktop_config.json`

Add the server configuration:

```json
{
  "mcpServers": {
    "llm-image-analyzer": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/llm-image-analyzer-mcp",
        "run",
        "llm-image-analyzer-mcp"
      ],
      "env": {
        "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "your-api-key",
        "AZURE_OPENAI_MODEL": "gpt-5.2",
        "MCP_DEBUG": "false"
      }
    }
  }
}
```

**Important:** Replace `/path/to/llm-image-analyzer-mcp` with the actual absolute path to your cloned repository.

### Alternative: Using .env file

If you prefer to keep credentials in the `.env` file:

```json
{
  "mcpServers": {
    "llm-image-analyzer": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/llm-image-analyzer-mcp",
        "run",
        "llm-image-analyzer-mcp"
      ]
    }
  }
}
```

The server will automatically load variables from `.env` in the project directory.

### Restart Claude Desktop

After editing the config file, restart Claude Desktop completely:
- **macOS:** Quit and reopen the app
- **Windows:** Exit from system tray and restart
- **Linux:** Kill the process and restart

### Verify Installation

In Claude Desktop, type:
```
Can you use the analyze_images tool to describe this image: [paste or attach image]
```

Claude should show the `llm-image-analyzer` server is connected and use the tool.

## Cline (VS Code Extension)

### Configuration

1. Open VS Code settings (JSON format)
2. Add MCP server configuration:

```json
{
  "cline.mcpServers": {
    "llm-image-analyzer": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/llm-image-analyzer-mcp",
        "run",
        "llm-image-analyzer-mcp"
      ],
      "env": {
        "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "your-api-key",
        "AZURE_OPENAI_MODEL": "gpt-5.2"
      }
    }
  }
}
```

3. Reload VS Code window
4. Open Cline panel - the server should appear in available tools

## MCP Inspector (Testing)

For development and testing:

```bash
# Option 1: Direct command
npx @modelcontextprotocol/inspector uv --directory /path/to/llm-image-analyzer-mcp run llm-image-analyzer-mcp

# Option 2: From project directory
cd /path/to/llm-image-analyzer-mcp
npx @modelcontextprotocol/inspector uv run llm-image-analyzer-mcp
```

This opens a web interface at `http://localhost:5173` where you can:
- View available tools
- Test tool calls interactively
- Inspect request/response payloads
- Debug server issues

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Yes | - | Your Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | Yes | - | Your Azure OpenAI API key |
| `AZURE_OPENAI_MODEL` | No | `gpt-5.2` | Default model deployment name |
| `AZURE_OPENAI_API_VERSION` | No | `2024-12-01-preview` | Azure OpenAI API version |
| `MCP_DEBUG` | No | `false` | Enable debug mode with stack traces |

## Troubleshooting

### Server Not Appearing in Client

1. **Check config file path is correct:**
   ```bash
   # Verify the path exists
   ls -la /path/to/llm-image-analyzer-mcp
   ```

2. **Verify uv is installed:**
   ```bash
   which uv
   uv --version
   ```

3. **Test server manually:**
   ```bash
   cd /path/to/llm-image-analyzer-mcp
   uv run llm-image-analyzer-mcp
   ```
   Should show FastMCP banner without errors.

4. **Check client logs:**
   - **Claude Desktop (macOS):** `~/Library/Logs/Claude/`
   - **Claude Desktop (Windows):** `%APPDATA%\Claude\logs\`
   - **Claude Desktop (Linux):** `~/.config/Claude/logs/`

### "Azure OpenAI not configured" Error

The server requires valid Azure OpenAI credentials. Check:

1. `.env` file exists in project root
2. `AZURE_OPENAI_ENDPOINT` is set correctly
3. `AZURE_OPENAI_API_KEY` is valid
4. Or pass these via `env` in MCP config

### "Image not found" Error

- Use absolute paths for local images
- Or use `~` for home directory (expands automatically)
- Or use URLs for remote images
- Verify file exists: `ls -la /path/to/image.jpg`

### Debug Mode

Enable detailed logging:

```json
{
  "env": {
    "MCP_DEBUG": "true"
  }
}
```

Errors will include full stack traces in tool responses.

## Example Usage in Claude Desktop

Once configured, you can ask Claude:

**Compare screenshots:**
```
I have two screenshots at ~/Desktop/before.png and ~/Desktop/after.png. 
Can you analyze what changed between them?
```

**Describe an image:**
```
Please describe this image in detail: https://example.com/photo.jpg
```

**Extract text:**
```
Extract all text from this document: ~/Documents/receipt.png
```

**Analyze multiple images:**
```
Compare these three product photos and tell me which one has the best composition:
- ~/photos/product1.jpg
- ~/photos/product2.jpg  
- ~/photos/product3.jpg
```

Claude will automatically use the `analyze_images` tool to process your request.

## Security Best Practices

1. **Never commit `.env` file** - it's in `.gitignore` by default
2. **Use environment-specific configs** - separate dev/prod credentials
3. **Rotate API keys regularly** - especially if exposed
4. **Use least-privilege keys** - Azure OpenAI keys with minimal required permissions
5. **Monitor usage** - check Azure portal for unexpected API calls

## Performance Tips

1. **Use `detail="low"`** for faster, cheaper analysis of simple images
2. **Set `max_tokens`** to limit response length when you need concise answers
3. **Use URLs when possible** - avoids base64 encoding overhead
4. **Batch related images** - analyze multiple images in one call when comparing

## Updates

To update the server:

```bash
cd /path/to/llm-image-analyzer-mcp
git pull
uv sync
```

Restart your MCP client after updating.

## Support

- **Issues:** https://github.com/tsoernes/llm-image-analyzer-mcp/issues
- **Documentation:** See [README.md](../README.md) and [examples/](../examples/)