"""
LLM Image Analyzer MCP Server

FastMCP server for analyzing images using Azure OpenAI vision models.
"""

__version__ = "0.1.0"

from llm_image_analyzer_mcp.server import main, mcp

__all__ = ["main", "mcp", "__version__"]
