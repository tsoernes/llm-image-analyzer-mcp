"""
Test script for analyzing a swan image using the LLM Image Analyzer MCP Server.

This test verifies that the analyze_images tool can correctly identify
a swan in the provided image URL.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm_image_analyzer_mcp.core import analyze_images_impl as analyze_images


async def test_analyze_swan_image():
    """Test analyzing a swan image from URL."""

    print("=" * 80)
    print("Testing LLM Image Analyzer with Swan Image")
    print("=" * 80)
    print()

    # Test image URL - direct Pexels image (publicly accessible)
    image_url = "https://images.pexels.com/photos/67287/swan-bird-animal-water-67287.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500"

    print(f"Image URL: {image_url}")
    print()

    # Test with string (not array) - testing new feature
    print("Testing with single string image_paths parameter...")
    print()

    result = await analyze_images(
        prompt="Describe what you see in this image. What animal is shown?",
        image_paths=image_url,  # Single string (not array)
        reasoning_effort="high",
    )

    # Check for errors
    if "error" in result:
        print("❌ ERROR occurred:")
        print(f"   Error: {result['error']}")
        print(f"   Type: {result['error_type']}")
        if "traceback" in result:
            print(f"\n{result['traceback']}")
        return False

    # Display results
    print("✅ Analysis completed successfully!")
    print()
    print(f"Model: {result['model']}")

    if "usage" in result:
        usage = result["usage"]
        print(f"Token Usage:")
        print(f"  - Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
        print(f"  - Completion tokens: {usage.get('completion_tokens', 'N/A')}")
        print(f"  - Total tokens: {usage.get('total_tokens', 'N/A')}")

    print()
    print("=" * 80)
    print("Analysis Result:")
    print("=" * 80)
    print(result["analysis"])
    print("=" * 80)
    print()

    # Assert that "swan" is in the response (case-insensitive)
    analysis_lower = result["analysis"].lower()

    if "swan" in analysis_lower:
        print("✅ PASS: 'swan' found in analysis!")
        print()
        return True
    else:
        print("❌ FAIL: 'swan' NOT found in analysis!")
        print()
        print("Searching for related terms...")

        # Check for related terms
        related_terms = ["bird", "waterfowl", "white", "water", "lake", "pond"]
        found_terms = [term for term in related_terms if term in analysis_lower]

        if found_terms:
            print(f"   Found related terms: {', '.join(found_terms)}")
        else:
            print("   No related terms found either.")

        print()
        return False


async def test_analyze_swan_array():
    """Test analyzing a swan image from URL using array format."""

    print()
    print("=" * 80)
    print("Testing with Array Format (backward compatibility)")
    print("=" * 80)
    print()

    # Same accessible image URL
    image_url = "https://images.pexels.com/photos/67287/swan-bird-animal-water-67287.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500"

    print("Testing with array image_paths parameter...")
    print()

    result = await analyze_images(
        prompt="What type of bird is this?",
        image_paths=[image_url],  # Array format
        max_tokens=100,
        reasoning_effort="medium",
    )

    if "error" in result:
        print("❌ ERROR occurred:")
        print(f"   Error: {result['error']}")
        return False

    print("✅ Analysis completed!")
    print(f"\nBrief analysis: {result['analysis'][:200]}...")

    # Check for swan
    if "swan" in result["analysis"].lower():
        print("\n✅ PASS: 'swan' found in analysis!")
        return True
    else:
        print("\n⚠️  WARNING: 'swan' not found, but analysis completed")
        return False


async def main():
    """Run all tests."""
    print("\n🧪 LLM Image Analyzer Test Suite\n")

    # Check if .env is configured
    import os

    from dotenv import load_dotenv

    load_dotenv()

    model = os.getenv("MODEL", "azure:gpt-5.2")

    if model.startswith("azure:"):
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")

        if not endpoint or not api_key:
            print("⚠️  WARNING: Azure OpenAI credentials not configured!")
            print("   Please configure .env file with:")
            print("   - AZURE_OPENAI_ENDPOINT")
            print("   - AZURE_OPENAI_API_KEY")
            print()
            print("   OR switch to another provider:")
            print("   - MODEL=openai:gpt-4o (requires OPENAI_API_KEY)")
            print("   - MODEL=anthropic:claude-sonnet-4 (requires ANTHROPIC_API_KEY)")
            print()
            return False

    print(f"Using model: {model}")
    print()

    # Run tests
    results = []

    # Test 1: Single string format
    test1_pass = await test_analyze_swan_image()
    results.append(("Swan Analysis (string format)", test1_pass))

    # Test 2: Array format (backward compatibility)
    test2_pass = await test_analyze_swan_array()
    results.append(("Swan Analysis (array format)", test2_pass))

    # Summary
    print()
    print("=" * 80)
    print("Test Summary")
    print("=" * 80)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print()
    print(f"Results: {total_passed}/{total_tests} tests passed")
    print("=" * 80)
    print()

    return all(passed for _, passed in results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
