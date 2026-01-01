"""
Core functionality for image analysis - testable without MCP decoration.

This module contains the core analyze_images_impl function that can be
tested independently of the FastMCP framework.
"""

import asyncio
import logging
import os
import traceback
from pathlib import Path
from typing import Any

import httpx
from PIL import Image
from pydantic_ai import Agent, BinaryContent, ImageUrl, ModelSettings

logger = logging.getLogger(__name__)

# Debug mode control
DEBUG_MODE = os.getenv("MCP_DEBUG", "false").lower() in ("true", "1", "yes")


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


async def _prepare_image_for_pydantic(image_path: str) -> ImageUrl | BinaryContent:
    """
    Prepare image for PydanticAI agent.

    Args:
        image_path: Local file path or URL

    Returns:
        ImageUrl for URLs, BinaryContent for local files
    """
    if _is_url(image_path):
        # Validate URL
        await _validate_url(image_path)
        logger.info(f"Using image URL: {image_path}")
        return ImageUrl(url=image_path)
    else:
        # Load local file
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

        # Determine MIME type from file extension
        ext = path.suffix.lower()
        mime_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        media_type = mime_type_map.get(ext, "image/jpeg")

        # Read binary content
        with open(path, "rb") as f:
            data = f.read()

        logger.info(f"Using local image: {image_path} ({len(data)} bytes)")
        return BinaryContent(data=data, media_type=media_type)


def _is_gpt5_model(model_name: str) -> bool:
    """Check if model is a GPT-5 variant (which uses max_completion_tokens)."""
    return "gpt-5" in model_name.lower()


async def analyze_images_impl(
    prompt: str,
    image_paths: str | list[str],
    model: str | None = None,
    max_tokens: int | None = None,
    reasoning_effort: str = "high",
    output_schema: dict | None = None,
) -> dict[str, Any]:
    """
    Core implementation of image analysis - testable without MCP decoration.

    This is the actual implementation that can be tested directly.
    The server.py file wraps this with @mcp.tool() decorator.

    Args:
        prompt: The question or instruction for analyzing the image(s)
        image_paths: Single image path (string) or multiple paths (list)
        model: Model identifier (format: "provider:model-name")
        max_tokens: Maximum tokens in response (auto-converts for GPT-5)
        reasoning_effort: Model reasoning effort ("low", "medium", "high")
        output_schema: Optional JSON schema for structured output
                      When provided, model returns data matching the schema

    Returns:
        Dictionary containing analysis results or error information
    """
    try:
        # Get environment configuration
        default_model = os.getenv("MODEL", "azure:gpt-5.2")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")

        # Validate inputs
        if not prompt or not prompt.strip():
            return {
                "error": "Prompt cannot be empty. Please provide a question or instruction for analyzing the image(s).",
                "error_type": "ValueError",
            }

        # Normalize image_paths to list
        if isinstance(image_paths, str):
            image_paths = [image_paths]

        if not image_paths or len(image_paths) == 0:
            return {
                "error": "At least one image path is required. Provide local file paths or URLs.",
                "error_type": "ValueError",
            }

        if reasoning_effort not in ("low", "medium", "high"):
            return {
                "error": f"Invalid reasoning_effort: {reasoning_effort}. Must be 'low', 'medium', or 'high'.",
                "error_type": "ValueError",
            }

        # Determine model to use
        model_name = model or default_model
        logger.info(f"Using model: {model_name}")

        # Validate Azure configuration if using Azure model
        if model_name.startswith("azure:"):
            if not azure_endpoint or not azure_api_key:
                return {
                    "error": (
                        "Azure OpenAI not configured. Please set AZURE_OPENAI_ENDPOINT "
                        "and AZURE_OPENAI_API_KEY in .env file or use a different model provider "
                        "(e.g., 'openai:gpt-4o', 'anthropic:claude-sonnet-4')."
                    ),
                    "error_type": "ConfigurationError",
                }

        # Prepare images for PydanticAI
        logger.info(f"Preparing {len(image_paths)} image(s) for analysis")
        images = await asyncio.gather(
            *[_prepare_image_for_pydantic(path) for path in image_paths]
        )

        # Build message content: prompt followed by images
        message_parts: list[str | ImageUrl | BinaryContent] = [prompt] + images

        # Build model settings
        model_settings_kwargs: dict[str, Any] = {}

        # Handle max_tokens vs max_completion_tokens
        if max_tokens is not None:
            if _is_gpt5_model(model_name):
                # GPT-5 models use max_completion_tokens
                model_settings_kwargs["max_completion_tokens"] = max_tokens
                logger.info(f"Using max_completion_tokens={max_tokens} for GPT-5 model")
            else:
                # Other models use max_tokens
                model_settings_kwargs["max_tokens"] = max_tokens
                logger.info(f"Using max_tokens={max_tokens}")

        # Note: reasoning_effort is not a standard ModelSettings parameter
        # For models that support it (like GPT-5), it would be passed differently
        # We log it but don't include it in settings for now
        logger.info(f"Reasoning effort: {reasoning_effort}")

        model_settings = (
            ModelSettings(**model_settings_kwargs) if model_settings_kwargs else None
        )

        # Create agent with the specified model
        # If output_schema provided, use result_type for structured output
        if output_schema:
            from pydantic import create_model

            # Create a dynamic Pydantic model from the JSON schema
            # Convert JSON schema to Pydantic field definitions
            fields = {}
            if "properties" in output_schema:
                for field_name, field_def in output_schema["properties"].items():
                    field_type = str  # Default to string
                    if field_def.get("type") == "number":
                        field_type = float
                    elif field_def.get("type") == "integer":
                        field_type = int
                    elif field_def.get("type") == "boolean":
                        field_type = bool
                    elif field_def.get("type") == "array":
                        field_type = list
                    elif field_def.get("type") == "object":
                        field_type = dict

                    # Check if field is required
                    is_required = field_name in output_schema.get("required", [])
                    if is_required:
                        fields[field_name] = (field_type, ...)
                    else:
                        fields[field_name] = (field_type | None, None)

            # Create dynamic model
            DynamicResultModel = create_model("DynamicResult", **fields)
            agent = Agent(
                model_name,
                result_type=DynamicResultModel,
                model_settings=model_settings,
            )
        else:
            agent = Agent(model_name, model_settings=model_settings)

        logger.info(
            f"Sending request: {len(image_paths)} images, "
            f"reasoning_effort={reasoning_effort}"
        )

        # Run the agent
        result = await agent.run(message_parts)

        # Build response
        if output_schema:
            # For structured output, return the parsed data
            response = {
                "data": result.output.model_dump()
                if hasattr(result.output, "model_dump")
                else result.output,
                "model": model_name,
            }
        else:
            # For text output, return as analysis
            response = {
                "analysis": result.output,
                "model": model_name,
            }

        # Include usage information if available
        if hasattr(result, "usage") and result.usage:
            usage_dict = {}
            if hasattr(result.usage, "prompt_tokens"):
                usage_dict["prompt_tokens"] = result.usage.prompt_tokens
            if hasattr(result.usage, "completion_tokens"):
                usage_dict["completion_tokens"] = result.usage.completion_tokens
            if hasattr(result.usage, "total_tokens"):
                usage_dict["total_tokens"] = result.usage.total_tokens

            if usage_dict:
                response["usage"] = usage_dict
                logger.info(
                    f"Analysis complete: {usage_dict.get('total_tokens', 'unknown')} tokens"
                )

        return response

    except Exception as e:
        return _format_error(e)
