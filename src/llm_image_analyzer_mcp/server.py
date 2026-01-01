"""
LLM Image Analyzer MCP Server

FastMCP server for analyzing images using vision models through PydanticAI.
Supports Azure OpenAI, OpenAI, Anthropic, and other providers via PydanticAI's
model-agnostic interface.
"""

import logging
import os

from dotenv import load_dotenv
from fastmcp import FastMCP

from llm_image_analyzer_mcp.core import analyze_images_impl

# Load environment variables from .env file
load_dotenv()

# Debug mode control
DEBUG_MODE = os.getenv("MCP_DEBUG", "false").lower() in ("true", "1", "yes")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("LLM Image Analyzer")

# Model configuration
DEFAULT_MODEL = os.getenv("MODEL", "azure:gpt-5.2")

# Azure OpenAI configuration (if using Azure)
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

# Validate Azure configuration if using Azure model
if DEFAULT_MODEL.startswith("azure:"):
    if not AZURE_OPENAI_ENDPOINT:
        logger.warning("AZURE_OPENAI_ENDPOINT not set - Azure models will fail")
    if not AZURE_OPENAI_API_KEY:
        logger.warning("AZURE_OPENAI_API_KEY not set - Azure models will fail")


@mcp.tool()
async def analyze_images(
    prompt: str,
    image_paths: str | list[str],
    model: str | None = None,
    max_tokens: int | None = None,
    reasoning_effort: str = "high",
) -> dict:
    """
    Analyze one or more images using vision models via PydanticAI.

    This tool sends a custom prompt along with one or more images to a vision model
    and returns the model's analysis. Supports multiple providers through PydanticAI:
    - Azure OpenAI (azure:gpt-5.2, azure:gpt-4o)
    - OpenAI (openai:gpt-4o, openai:gpt-4-turbo)
    - Anthropic (anthropic:claude-sonnet-4)
    - And more via PydanticAI's model-agnostic interface

    Common use cases:
    - Compare two or more images
    - Describe what's in an image
    - Extract text from images (OCR)
    - Identify objects, people, or scenes
    - Answer questions about image content

    Args:
        prompt: The question or instruction for analyzing the image(s).
                Examples:
                - "What are the differences between these two screenshots?"
                - "Describe what you see in this image"
                - "Extract all text from this document"
                - "What brand logo is visible in this image?"

        image_paths: List of image paths (local files or URLs).
                     Local paths: "/path/to/image.jpg", "~/photos/pic.png"
                     URLs: "https://example.com/image.jpg"
                     Supports: JPEG, PNG, GIF, WebP

        model: Model identifier (optional).
               Format: "provider:model-name"
               Examples:
               - "azure:gpt-5.2" (default if MODEL env var not set)
               - "openai:gpt-4o"
               - "anthropic:claude-sonnet-4"
               - "azure:gpt-4o"

               Defaults to MODEL env var or "azure:gpt-5.2".

        max_tokens: Maximum tokens in response (optional).
                   None = no limit (uses model default).
                   Note: For GPT-5 models, this is automatically converted to
                   max_completion_tokens as required by the API.
                   Use lower values for concise responses, higher for detailed analysis.

        reasoning_effort: Model reasoning effort (default: "high").
                         Note: Support varies by model.
                         - "low": Faster, less thorough
                         - "medium": Balanced
                         - "high": Most thorough, best quality (recommended for GPT-5)

    Returns:
        Dictionary containing:
        - analysis: The model's text response
        - model: Model identifier used
        - usage: Token usage information (if available)
          - prompt_tokens: Tokens in the prompt
          - completion_tokens: Tokens in the response
          - total_tokens: Total tokens used

    Raises:
        Returns error dict with details in debug mode (MCP_DEBUG=true)

    Examples:
        # Compare two screenshots
        analyze_images(
            prompt="What changed between these two screenshots?",
            image_paths=["screenshot1.png", "screenshot2.png"]
        )

        # Describe an image from URL
        analyze_images(
            prompt="Describe this image in detail",
            image_paths="https://example.com/photo.jpg"
        )

        # Extract text with OpenAI
        analyze_images(
            prompt="Extract all visible text",
            image_paths=["document.png"],
            model="openai:gpt-4o",
            max_tokens=500
        )

        # Use Anthropic Claude
        analyze_images(
            prompt="Analyze this architectural design",
            image_paths=["~/designs/floor_plan.jpg"],
            model="anthropic:claude-sonnet-4"
        )
    """
    # Delegate to core implementation
    return await analyze_images_impl(
        prompt=prompt,
        image_paths=image_paths,
        model=model,
        max_tokens=max_tokens,
        reasoning_effort=reasoning_effort,
    )


def main():
    """Entry point for the MCP server."""
    logger.info("Starting LLM Image Analyzer MCP Server (PydanticAI)")
    logger.info(f"Debug mode: {DEBUG_MODE}")
    logger.info(f"Default model: {DEFAULT_MODEL}")

    if DEFAULT_MODEL.startswith("azure:"):
        logger.info(f"Azure endpoint configured: {bool(AZURE_OPENAI_ENDPOINT)}")

    # Run the server (stdio transport by default)
    mcp.run()


if __name__ == "__main__":
    main()
