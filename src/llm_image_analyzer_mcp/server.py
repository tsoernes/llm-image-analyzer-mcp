"""
LLM Image Analyzer MCP Server

FastMCP server for analyzing images using Azure OpenAI vision models.
Supports both local file paths and URLs, with configurable model parameters.
"""

import asyncio
import base64
import logging
import os
import traceback
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from openai import AsyncAzureOpenAI
from PIL import Image

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

# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("AZURE_OPENAI_MODEL", "gpt-5.2")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

# Validate required environment variables
if not AZURE_OPENAI_ENDPOINT:
    logger.error("AZURE_OPENAI_ENDPOINT not set in environment")
if not AZURE_OPENAI_API_KEY:
    logger.error("AZURE_OPENAI_API_KEY not set in environment")


def _format_error(e: Exception) -> dict[str, Any]:
    """
    Format exception based on debug mode setting.

    In debug mode (MCP_DEBUG=true):
        Returns full stack trace with line numbers
    In production mode:
        Returns compact error message only
    """
    error_dict = {
        "error": str(e),
        "error_type": type(e).__name__,
        "debug_mode": DEBUG_MODE,
    }

    if DEBUG_MODE:
        error_dict["traceback"] = traceback.format_exc()
        logger.error(f"Tool error with traceback:\n{traceback.format_exc()}")
    else:
        logger.error(f"Tool error: {type(e).__name__}: {e}")

    return error_dict


async def _encode_image_from_path(image_path: str) -> str:
    """
    Encode a local image file to base64.

    Args:
        image_path: Path to local image file

    Returns:
        Base64-encoded image string

    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If file is not a valid image format
    """
    path = Path(image_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(
            f"Image not found at path: {image_path}. "
            f"Please check that the file exists and the path is correct."
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {image_path}. Please provide a path to an image file."
        )

    # Validate image format by attempting to open with PIL
    try:
        with Image.open(path) as img:
            logger.debug(
                f"Image format: {img.format}, size: {img.size}, mode: {img.mode}"
            )
    except Exception as e:
        raise ValueError(
            f"Invalid image file at {image_path}. "
            f"Supported formats: JPEG, PNG, GIF, WebP. Error: {e}"
        )

    # Read and encode
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
        logger.debug(f"Encoded image from {image_path} ({len(encoded)} chars)")
        return encoded


async def _validate_url(url: str) -> bool:
    """
    Validate that a URL is accessible and points to an image.

    Args:
        url: URL to validate

    Returns:
        True if URL is valid and accessible

    Raises:
        ValueError: If URL is invalid or inaccessible
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.head(url, follow_redirects=True)

            if response.status_code != 200:
                raise ValueError(
                    f"URL returned status {response.status_code}: {url}. "
                    f"Please check that the URL is correct and accessible."
                )

            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                logger.warning(
                    f"URL does not appear to be an image (content-type: {content_type}): {url}"
                )

            logger.debug(f"Validated URL: {url} (content-type: {content_type})")
            return True

    except httpx.TimeoutException:
        raise ValueError(
            f"Timeout while accessing URL: {url}. "
            f"Please check your network connection and try again."
        )
    except httpx.RequestError as e:
        raise ValueError(f"Failed to access URL: {url}. Error: {e}")


def _is_url(path: str) -> bool:
    """Check if a string is a URL."""
    return path.startswith(("http://", "https://"))


async def _prepare_image_content(image_path: str, detail: str) -> dict[str, Any]:
    """
    Prepare image content for OpenAI API.

    Args:
        image_path: Local file path or URL
        detail: Image detail level ("auto", "low", "high")

    Returns:
        Image content dict for OpenAI API
    """
    if _is_url(image_path):
        # Validate URL
        await _validate_url(image_path)
        logger.info(f"Using image URL: {image_path}")
        return {
            "type": "image_url",
            "image_url": {
                "url": image_path,
                "detail": detail,
            },
        }
    else:
        # Encode local file
        encoded_image = await _encode_image_from_path(image_path)
        logger.info(f"Using local image: {image_path}")

        # Determine MIME type from file extension
        ext = Path(image_path).suffix.lower()
        mime_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        mime_type = mime_type_map.get(ext, "image/jpeg")

        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{encoded_image}",
                "detail": detail,
            },
        }


@mcp.tool()
async def analyze_images(
    prompt: str,
    image_paths: list[str],
    model: str | None = None,
    max_tokens: int | None = None,
    detail: str = "auto",
    reasoning_effort: str = "high",
) -> dict[str, Any]:
    """
    Analyze one or more images using Azure OpenAI vision models.

    This tool sends a custom prompt along with one or more images to an Azure OpenAI
    vision model (like GPT-4o or GPT-5.2) and returns the model's analysis.

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

        model: Azure OpenAI model deployment name (optional).
               Defaults to AZURE_OPENAI_MODEL env var or "gpt-5.2".
               Override to use a different model for specific tasks.

        max_tokens: Maximum tokens in response (optional).
                   None = no limit (uses model default).
                   Use lower values for concise responses, higher for detailed analysis.

        detail: Image detail level for API (default: "auto").
                - "auto": Let the model decide
                - "low": Faster, cheaper, less detail (512x512)
                - "high": Slower, more expensive, more detail (2048x2048)

        reasoning_effort: Model reasoning effort (default: "high").
                         - "low": Faster, less thorough
                         - "medium": Balanced
                         - "high": Most thorough, best quality

    Returns:
        Dictionary containing:
        - analysis: The model's text response
        - model: Model name used
        - prompt_tokens: Number of tokens in prompt (if available)
        - completion_tokens: Number of tokens in response (if available)
        - total_tokens: Total tokens used (if available)

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
            image_paths=["https://example.com/photo.jpg"],
            detail="high"
        )

        # Extract text with custom model
        analyze_images(
            prompt="Extract all visible text",
            image_paths=["document.png"],
            model="gpt-4o",
            max_tokens=500
        )
    """
    try:
        # Validate environment
        if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
            return {
                "error": "Azure OpenAI not configured. Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env file.",
                "error_type": "ConfigurationError",
            }

        # Validate inputs
        if not prompt or not prompt.strip():
            return {
                "error": "Prompt cannot be empty. Please provide a question or instruction for analyzing the image(s).",
                "error_type": "ValueError",
            }

        if not image_paths or len(image_paths) == 0:
            return {
                "error": "At least one image path is required. Provide local file paths or URLs.",
                "error_type": "ValueError",
            }

        if detail not in ("auto", "low", "high"):
            return {
                "error": f"Invalid detail level: {detail}. Must be 'auto', 'low', or 'high'.",
                "error_type": "ValueError",
            }

        if reasoning_effort not in ("low", "medium", "high"):
            return {
                "error": f"Invalid reasoning_effort: {reasoning_effort}. Must be 'low', 'medium', or 'high'.",
                "error_type": "ValueError",
            }

        # Determine model to use
        model_name = model or DEFAULT_MODEL
        logger.info(f"Using model: {model_name}")

        # Initialize Azure OpenAI client
        client = AsyncAzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_API_VERSION,
        )

        # Prepare image content
        logger.info(f"Preparing {len(image_paths)} image(s) for analysis")
        image_contents = await asyncio.gather(
            *[_prepare_image_content(path, detail) for path in image_paths]
        )

        # Build message content (text prompt + images)
        message_content = [{"type": "text", "text": prompt}] + image_contents

        # Prepare API call parameters
        api_params = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": message_content,
                }
            ],
        }

        # Add optional parameters
        if max_tokens is not None:
            api_params["max_tokens"] = max_tokens

        # Add reasoning_effort (if supported by model)
        if reasoning_effort:
            api_params["reasoning_effort"] = reasoning_effort

        logger.info(
            f"Sending request to Azure OpenAI: {len(image_paths)} images, detail={detail}, reasoning_effort={reasoning_effort}"
        )

        # Call Azure OpenAI API
        response = await client.chat.completions.create(**api_params)

        # Extract response
        analysis = response.choices[0].message.content

        # Build result
        result = {
            "analysis": analysis,
            "model": model_name,
        }

        # Include token usage if available
        if response.usage:
            result["prompt_tokens"] = response.usage.prompt_tokens
            result["completion_tokens"] = response.usage.completion_tokens
            result["total_tokens"] = response.usage.total_tokens
            logger.info(
                f"Analysis complete: {response.usage.total_tokens} tokens "
                f"(prompt: {response.usage.prompt_tokens}, completion: {response.usage.completion_tokens})"
            )

        return result

    except Exception as e:
        return _format_error(e)


def main():
    """Entry point for the MCP server."""
    logger.info("Starting LLM Image Analyzer MCP Server")
    logger.info(f"Debug mode: {DEBUG_MODE}")
    logger.info(f"Default model: {DEFAULT_MODEL}")
    logger.info(f"Azure endpoint configured: {bool(AZURE_OPENAI_ENDPOINT)}")

    # Run the server (stdio transport by default)
    mcp.run()


if __name__ == "__main__":
    main()
