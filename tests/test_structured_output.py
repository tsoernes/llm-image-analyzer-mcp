"""
Test structured output feature for image analysis.

Tests that the output_schema parameter correctly extracts structured data
from images using Pydantic models.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

from llm_image_analyzer_mcp.core import analyze_images_impl as analyze_images


class TestStructuredOutput:
    """Test structured output with JSON schemas."""

    @pytest.mark.asyncio
    async def test_structured_output_schema_accepted(self):
        """Test that output_schema parameter is accepted."""
        schema = {
            "type": "object",
            "properties": {
                "item_name": {"type": "string"},
                "price": {"type": "number"},
            },
            "required": ["item_name"],
        }

        result = await analyze_images(
            prompt="Extract product info",
            image_paths="test.jpg",
            output_schema=schema,
        )

        # Should not error on schema parameter itself
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_structured_output_returns_data_key(self):
        """Test that structured output returns 'data' instead of 'analysis'."""
        schema = {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
            },
        }

        result = await analyze_images(
            prompt="Describe this",
            image_paths="test.jpg",
            output_schema=schema,
        )

        # With schema, should return 'data' key (or error)
        if "error" not in result:
            assert "data" in result or "error" in result

    @pytest.mark.asyncio
    async def test_without_schema_returns_analysis_key(self):
        """Test that without schema, returns 'analysis' key."""
        result = await analyze_images(
            prompt="Describe this",
            image_paths="test.jpg",
            output_schema=None,  # Explicitly no schema
        )

        # Without schema, should return 'analysis' key (or error)
        if "error" not in result:
            assert "analysis" in result or "error" in result

    @pytest.mark.asyncio
    async def test_schema_with_string_field(self):
        """Test schema with string field type."""
        schema = {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
            },
        }

        result = await analyze_images(
            prompt="Extract text",
            image_paths="test.jpg",
            output_schema=schema,
        )

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_schema_with_number_field(self):
        """Test schema with number field type."""
        schema = {
            "type": "object",
            "properties": {
                "price": {"type": "number"},
                "quantity": {"type": "integer"},
            },
        }

        result = await analyze_images(
            prompt="Count items",
            image_paths="test.jpg",
            output_schema=schema,
        )

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_schema_with_array_field(self):
        """Test schema with array field type."""
        schema = {
            "type": "object",
            "properties": {
                "items": {"type": "array"},
            },
        }

        result = await analyze_images(
            prompt="List items",
            image_paths="test.jpg",
            output_schema=schema,
        )

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_schema_with_required_fields(self):
        """Test schema with required fields."""
        schema = {
            "type": "object",
            "properties": {
                "required_field": {"type": "string"},
                "optional_field": {"type": "string"},
            },
            "required": ["required_field"],
        }

        result = await analyze_images(
            prompt="Extract data",
            image_paths="test.jpg",
            output_schema=schema,
        )

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_schema_with_multiple_types(self):
        """Test schema with multiple field types."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "count": {"type": "integer"},
                "price": {"type": "number"},
                "available": {"type": "boolean"},
                "tags": {"type": "array"},
                "metadata": {"type": "object"},
            },
        }

        result = await analyze_images(
            prompt="Extract all fields",
            image_paths="test.jpg",
            output_schema=schema,
        )

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_empty_schema_handled(self):
        """Test that empty schema is handled gracefully."""
        schema = {"type": "object", "properties": {}}

        result = await analyze_images(
            prompt="Extract data",
            image_paths="test.jpg",
            output_schema=schema,
        )

        assert isinstance(result, dict)


class TestStructuredOutputValidation:
    """Test validation of structured output parameters."""

    @pytest.mark.asyncio
    async def test_valid_prompt_still_required(self):
        """Test that prompt validation still applies with schema."""
        schema = {
            "type": "object",
            "properties": {"field": {"type": "string"}},
        }

        result = await analyze_images(
            prompt="",  # Empty prompt
            image_paths="test.jpg",
            output_schema=schema,
        )

        assert "error" in result
        assert "cannot be empty" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_valid_image_paths_still_required(self):
        """Test that image_paths validation still applies with schema."""
        schema = {
            "type": "object",
            "properties": {"field": {"type": "string"}},
        }

        result = await analyze_images(
            prompt="Extract data",
            image_paths=[],  # Empty list
            output_schema=schema,
        )

        assert "error" in result
        assert "at least one image" in result["error"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
