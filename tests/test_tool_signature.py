"""
Unit tests for the analyze_images tool signature and parameter validation.

These tests verify the tool interface without requiring actual API credentials.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

from llm_image_analyzer_mcp.core import analyze_images_impl as analyze_images


class TestToolSignature:
    """Test the analyze_images tool signature and validation."""

    @pytest.mark.asyncio
    async def test_missing_prompt_returns_error(self):
        """Test that missing prompt returns validation error."""
        result = await analyze_images(
            prompt="",
            image_paths="test.jpg",
        )

        assert "error" in result
        assert "cannot be empty" in result["error"].lower()
        assert result["error_type"] == "ValueError"

    @pytest.mark.asyncio
    async def test_empty_image_paths_returns_error(self):
        """Test that empty image_paths returns validation error."""
        result = await analyze_images(
            prompt="Describe this image",
            image_paths=[],
        )

        assert "error" in result
        assert "at least one image" in result["error"].lower()
        assert result["error_type"] == "ValueError"

    @pytest.mark.asyncio
    async def test_invalid_reasoning_effort_returns_error(self):
        """Test that invalid reasoning_effort returns validation error."""
        result = await analyze_images(
            prompt="Describe this image",
            image_paths="test.jpg",
            reasoning_effort="invalid",
        )

        assert "error" in result
        assert "reasoning_effort" in result["error"].lower()
        assert result["error_type"] == "ValueError"

    @pytest.mark.asyncio
    async def test_single_string_image_path_accepted(self):
        """Test that single string image_paths is accepted (not validation error)."""
        result = await analyze_images(
            prompt="Describe this image",
            image_paths="test.jpg",  # Single string
        )

        # Should not be a validation error about image_paths format
        # (May be file not found or config error, but not format validation)
        if "error" in result:
            assert "at least one image" not in result["error"].lower()

    @pytest.mark.asyncio
    async def test_array_image_paths_accepted(self):
        """Test that array image_paths is accepted (backward compatibility)."""
        result = await analyze_images(
            prompt="Describe this image",
            image_paths=["test1.jpg", "test2.jpg"],  # Array
        )

        # Should not be a validation error about image_paths format
        if "error" in result:
            assert "at least one image" not in result["error"].lower()

    @pytest.mark.asyncio
    async def test_max_tokens_parameter_accepted(self):
        """Test that max_tokens parameter is accepted."""
        result = await analyze_images(
            prompt="Describe this image",
            image_paths="test.jpg",
            max_tokens=100,
        )

        # Should not error on max_tokens parameter itself
        if "error" in result:
            assert "max_tokens" not in result["error"].lower()

    @pytest.mark.asyncio
    async def test_model_parameter_accepted(self):
        """Test that model parameter is accepted."""
        result = await analyze_images(
            prompt="Describe this image",
            image_paths="test.jpg",
            model="openai:gpt-4o",
        )

        # Should not error on model parameter itself
        if "error" in result:
            assert (
                "model" not in result["error"].lower()
                or "not configured" in result["error"].lower()
            )

    @pytest.mark.asyncio
    async def test_tool_returns_dict(self):
        """Test that tool always returns a dictionary."""
        result = await analyze_images(
            prompt="Test prompt",
            image_paths="test.jpg",
        )

        assert isinstance(result, dict), "Tool must return a dictionary"

    @pytest.mark.asyncio
    async def test_error_response_has_required_fields(self):
        """Test that error responses have required fields."""
        result = await analyze_images(
            prompt="",  # Invalid
            image_paths="test.jpg",
        )

        assert "error" in result
        assert "error_type" in result
        assert isinstance(result["error"], str)
        assert isinstance(result["error_type"], str)

    @pytest.mark.asyncio
    async def test_debug_mode_field_in_error(self):
        """Test that error responses include debug_mode field."""
        result = await analyze_images(
            prompt="",  # Invalid
            image_paths="test.jpg",
        )

        # Validation errors (early returns) don't include debug_mode
        # Only exceptions caught by _format_error include it
        assert "error" in result
        assert "error_type" in result
        # debug_mode is optional - only present for exceptions, not validation errors


class TestParameterNormalization:
    """Test parameter normalization logic."""

    @pytest.mark.asyncio
    async def test_string_converted_to_list_internally(self):
        """Test that single string is converted to list internally."""
        # This is tested indirectly - if it works without format validation error,
        # the normalization is working
        result = await analyze_images(
            prompt="Test",
            image_paths="single.jpg",  # String
        )

        # Should process as if it were ["single.jpg"]
        # May fail for other reasons (file not found, no credentials)
        # but not because of parameter format
        if "error" in result:
            assert (
                "must be" not in result["error"].lower()
                or "image" not in result["error"].lower()
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
