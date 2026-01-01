# Zed Editor Setup Guide

This guide shows how to configure the LLM Image Analyzer MCP Server in Zed Editor.

## Prerequisites

1. **Zed Editor** installed with MCP support
2. **Server installed** and configured (see main README.md)
3. **Environment variables** configured in `.env` file

## Configuration

### 1. Open Zed Settings

Open your Zed settings file:
- **macOS/Linux**: `~/.config/zed/settings.json`
- **Windows**: `%APPDATA%\Zed\settings.json`

Or use the command palette: `Cmd/Ctrl+Shift+P` → "Open Settings"

### 2. Add MCP Server Configuration

Add the following to the `context_servers` section:

```json
{
  "context_servers": {
    "llm-image-analyzer": {
      "enabled": true,
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/home/torstein.sornes/code/llm-image-analyzer",
        "llm-image-analyzer-mcp"
      ],
      "env": {
        "MODEL": "azure:gpt-5.2",
        "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**Important:** Replace `/home/torstein.sornes/code/llm-image-analyzer` with your actual installation path.

### 3. Alternative: Use .env File

If you prefer to keep credentials in the `.env` file (recommended):

```json
{
  "context_servers": {
    "llm-image-analyzer": {
      "enabled": true,
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/llm-image-analyzer",
        "llm-image-analyzer-mcp"
      ]
    }
  }
}
```

The server will automatically load variables from `.env` in the project directory.

### 4. Complete Example with Multiple Providers

Example showing how to configure multiple model providers:

```json
{
  "context_servers": {
    "llm-image-analyzer": {
      "enabled": true,
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/home/user/code/llm-image-analyzer",
        "llm-image-analyzer-mcp"
      ],
      "env": {
        "MODEL": "azure:gpt-5.2",
        "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "your-azure-key",
        "OPENAI_API_KEY": "sk-your-openai-key",
        "ANTHROPIC_API_KEY": "sk-ant-your-anthropic-key",
        "MCP_DEBUG": "false"
      }
    }
  }
}
```

## Configuration Options

### Required Parameters

| Parameter | Description |
|-----------|-------------|
| `enabled` | Set to `true` to enable the server |
| `command` | Command to run (use `uv` for this server) |
| `args` | Arguments array with path to server |

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MODEL` | No | `azure:gpt-5.2` | Default model (format: `provider:model-name`) |
| `AZURE_OPENAI_ENDPOINT` | If using Azure | - | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | If using Azure | - | Azure OpenAI API key |
| `AZURE_OPENAI_API_VERSION` | No | `2024-12-01-preview` | Azure API version |
| `OPENAI_API_KEY` | If using OpenAI | - | OpenAI API key |
| `ANTHROPIC_API_KEY` | If using Anthropic | - | Anthropic API key |
| `MCP_DEBUG` | No | `false` | Enable debug mode with stack traces |

## Restart Zed

After editing the configuration:

1. Save the settings file
2. Restart Zed Editor completely
3. The server will appear in the context panel

## Verify Installation

### Check Server Status

1. Open Zed
2. Look for the context icon (usually in the right panel)
3. You should see "llm-image-analyzer" in the list of available servers
4. Check that it shows as "Connected" or "Active"

### Test the Tool

In Zed's chat interface, try:

```
Can you analyze this screenshot for me? /path/to/image.png
```

Or use the tool directly:
```
Use the analyze_images tool to describe what's in this image: ~/photos/test.jpg
```

## Troubleshooting

### Server Not Appearing

**Check the path:**
```bash
# Verify the path exists
ls -la /path/to/llm-image-analyzer

# Test the server manually
cd /path/to/llm-image-analyzer
uv run llm-image-analyzer-mcp
```

**Check Zed logs:**
- Look for errors in Zed's developer console
- Check server output in Zed's MCP panel

### "Command not found: uv"

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then restart your terminal and Zed.

### Environment Variables Not Loading

If using inline `env` in Zed config:
- Make sure keys are quoted strings
- Ensure no trailing commas in JSON
- Restart Zed after changes

If using `.env` file:
- Verify `.env` exists in project root
- Check file permissions: `chmod 600 .env`
- Ensure no syntax errors in `.env`

### "Azure OpenAI not configured" Error

Either:
1. Add Azure credentials to Zed config `env` section, OR
2. Ensure `.env` file has correct variables, OR
3. Switch to another provider in `MODEL` env var

### Server Crashes or Disconnects

Enable debug mode:
```json
"env": {
  "MCP_DEBUG": "true"
}
```

Then check Zed's MCP panel for detailed error messages.

## Usage Examples

Once configured, you can use the server in Zed's chat:

### Compare Screenshots
```
I have two screenshots - can you tell me what changed?
Image 1: ~/Desktop/before.png
Image 2: ~/Desktop/after.png
```

### Describe Image
```
Describe this image in detail: https://example.com/photo.jpg
```

### Extract Text
```
Extract all text from this document: ~/Documents/receipt.png
```

### Analyze with Specific Model
```
Use the analyze_images tool with model "openai:gpt-4o" to analyze ~/photo.jpg
```

## Advanced Configuration

### Debug Mode Always On

```json
"env": {
  "MCP_DEBUG": "true"
}
```

### Use Different Default Model

```json
"env": {
  "MODEL": "openai:gpt-4o"
}
```

### Custom API Versions

```json
"env": {
  "AZURE_OPENAI_API_VERSION": "2025-01-01-preview"
}
```

## Multiple Instances

You can configure multiple instances with different models:

```json
{
  "context_servers": {
    "image-analyzer-azure": {
      "enabled": true,
      "command": "uv",
      "args": ["run", "--directory", "/path/to/llm-image-analyzer", "llm-image-analyzer-mcp"],
      "env": {
        "MODEL": "azure:gpt-5.2"
      }
    },
    "image-analyzer-openai": {
      "enabled": true,
      "command": "uv",
      "args": ["run", "--directory", "/path/to/llm-image-analyzer", "llm-image-analyzer-mcp"],
      "env": {
        "MODEL": "openai:gpt-4o"
      }
    }
  }
}
```

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use .env file** for sensitive data (it's in `.gitignore`)
3. **Rotate API keys** regularly
4. **Use read-only keys** when possible
5. **Monitor usage** in provider dashboards

## Updating the Server

To update to the latest version:

```bash
cd /path/to/llm-image-analyzer
git pull
uv sync
```

Then restart Zed.

## Uninstalling

To remove the server from Zed:

1. Open `~/.config/zed/settings.json`
2. Remove the `llm-image-analyzer` entry from `context_servers`
3. Save and restart Zed

## Support

- **Issues**: https://github.com/tsoernes/llm-image-analyzer-mcp/issues
- **Documentation**: See [README.md](../README.md)
- **Zed MCP Docs**: https://zed.dev/docs/context-servers