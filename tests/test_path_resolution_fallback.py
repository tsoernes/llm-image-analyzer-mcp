"""
Test two-step path resolution fallback strategy.

Tests the _resolve_path_with_fallback function which implements:
1. First attempt: Try path relative to cwd
2. Second attempt: Strip first directory component and try again
"""

import os
import tempfile
from pathlib import Path

import pytest

from llm_image_analyzer_mcp.core import _resolve_path_with_fallback


@pytest.fixture
def temp_image_structure(tmp_path):
    """
    Create a temporary directory structure for testing:

    tmp_path/
        someproject/
            image1.jpg
        image2.jpg
        nested/
            deep/
                image3.jpg
    """
    # Create directories
    project_dir = tmp_path / "someproject"
    project_dir.mkdir()

    nested_dir = tmp_path / "nested" / "deep"
    nested_dir.mkdir(parents=True)

    # Create dummy image files
    image1 = project_dir / "image1.jpg"
    image1.write_bytes(b"fake jpg data 1")

    image2 = tmp_path / "image2.jpg"
    image2.write_bytes(b"fake jpg data 2")

    image3 = nested_dir / "image3.jpg"
    image3.write_bytes(b"fake jpg data 3")

    return {
        "tmp_path": tmp_path,
        "image1": image1,
        "image2": image2,
        "image3": image3,
    }


def test_absolute_path(temp_image_structure):
    """Test that absolute paths are returned as-is."""
    image1 = temp_image_structure["image1"]

    result = _resolve_path_with_fallback(str(image1))

    assert result.exists()
    assert result == image1.resolve()


def test_relative_path_exists_at_first_attempt(temp_image_structure, monkeypatch):
    """Test first attempt succeeds when path exists relative to cwd."""
    tmp_path = temp_image_structure["tmp_path"]
    image1 = temp_image_structure["image1"]

    # Change to tmp_path
    monkeypatch.chdir(tmp_path)

    # This should resolve on first attempt
    result = _resolve_path_with_fallback("someproject/image1.jpg")

    assert result.exists()
    assert result == image1.resolve()


def test_relative_path_fallback_to_second_attempt(temp_image_structure, monkeypatch):
    """
    Test second attempt succeeds when first fails.

    Scenario: User provides "someproject/image2.jpg" but image2.jpg
    is actually in the cwd, not in someproject/.
    """
    tmp_path = temp_image_structure["tmp_path"]
    image2 = temp_image_structure["image2"]

    # Change to tmp_path
    monkeypatch.chdir(tmp_path)

    # First attempt: tmp_path/someproject/image2.jpg (doesn't exist)
    # Second attempt: tmp_path/image2.jpg (exists)
    result = _resolve_path_with_fallback("someproject/image2.jpg")

    assert result.exists()
    assert result == image2.resolve()


def test_nested_path_fallback(temp_image_structure, monkeypatch):
    """Test fallback with nested paths (multiple directory components)."""
    tmp_path = temp_image_structure["tmp_path"]
    image3 = temp_image_structure["image3"]

    # Change to tmp_path
    monkeypatch.chdir(tmp_path)

    # This should resolve on first attempt (path exists)
    result = _resolve_path_with_fallback("nested/deep/image3.jpg")

    assert result.exists()
    assert result == image3.resolve()


def test_nested_path_strips_only_first_component(temp_image_structure, monkeypatch):
    """
    Test that fallback only strips the first directory component.

    If user provides "project/nested/deep/image3.jpg" and it doesn't exist,
    we should try "nested/deep/image3.jpg" (not "image3.jpg").
    """
    tmp_path = temp_image_structure["tmp_path"]
    image3 = temp_image_structure["image3"]

    # Change to tmp_path
    monkeypatch.chdir(tmp_path)

    # First attempt: tmp_path/project/nested/deep/image3.jpg (doesn't exist)
    # Second attempt: tmp_path/nested/deep/image3.jpg (exists)
    result = _resolve_path_with_fallback("project/nested/deep/image3.jpg")

    assert result.exists()
    assert result == image3.resolve()


def test_path_not_found_raises_error(temp_image_structure, monkeypatch):
    """Test that FileNotFoundError is raised when neither path exists."""
    tmp_path = temp_image_structure["tmp_path"]

    # Change to tmp_path
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError) as exc_info:
        _resolve_path_with_fallback("nonexistent/image.jpg")

    error_msg = str(exc_info.value)
    assert "Image not found" in error_msg
    assert "nonexistent/image.jpg" in error_msg


def test_single_component_path_no_fallback(temp_image_structure, monkeypatch):
    """
    Test that single-component paths don't trigger fallback.

    If path is just "image2.jpg" (no directory components), there's
    nothing to strip, so we only try once.
    """
    tmp_path = temp_image_structure["tmp_path"]
    image2 = temp_image_structure["image2"]

    # Change to tmp_path
    monkeypatch.chdir(tmp_path)

    result = _resolve_path_with_fallback("image2.jpg")

    assert result.exists()
    assert result == image2.resolve()


def test_single_component_path_not_found(temp_image_structure, monkeypatch):
    """Test single-component path that doesn't exist."""
    tmp_path = temp_image_structure["tmp_path"]

    # Change to tmp_path
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError) as exc_info:
        _resolve_path_with_fallback("nonexistent.jpg")

    error_msg = str(exc_info.value)
    assert "Image not found" in error_msg
    # Should NOT mention second attempt path since there's only one component
    # Check that " and /" pattern (indicating second path) is not present
    assert " and /" not in error_msg


def test_tilde_expansion(temp_image_structure, monkeypatch):
    """Test that tilde (~) is properly expanded."""
    image2 = temp_image_structure["image2"]

    # Create a file in the user's home directory
    home = Path.home()
    test_file = home / "test_image_resolution.jpg"
    test_file.write_bytes(b"test data")

    try:
        result = _resolve_path_with_fallback("~/test_image_resolution.jpg")

        assert result.exists()
        assert result == test_file.resolve()
    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()


def test_windows_style_paths_if_applicable(temp_image_structure, monkeypatch):
    """Test Windows-style paths on Windows systems."""
    if os.name != "nt":
        pytest.skip("Windows-specific test")

    tmp_path = temp_image_structure["tmp_path"]
    image2 = temp_image_structure["image2"]

    # Change to tmp_path
    monkeypatch.chdir(tmp_path)

    # Test with backslashes (Windows style)
    result = _resolve_path_with_fallback("someproject\\image2.jpg")

    assert result.exists()
    assert result == image2.resolve()


def test_symlink_resolution(temp_image_structure, tmp_path):
    """Test that symlinks are properly resolved."""
    image1 = temp_image_structure["image1"]

    # Create a symlink
    symlink_path = tmp_path / "link_to_image1.jpg"
    try:
        symlink_path.symlink_to(image1)
    except OSError:
        pytest.skip("System doesn't support symlinks")

    result = _resolve_path_with_fallback(str(symlink_path))

    assert result.exists()
    assert result == image1.resolve()


def test_real_world_scenario(temp_image_structure, monkeypatch):
    """
    Simulate real-world usage scenario.

    User is working in /home/user/code/ and provides path
    "llm-image-analyzer/tests/data/image.jpg" but the image
    is actually at /home/user/code/tests/data/image.jpg
    """
    tmp_path = temp_image_structure["tmp_path"]

    # Create structure
    tests_dir = tmp_path / "tests" / "data"
    tests_dir.mkdir(parents=True)

    real_image = tests_dir / "image.jpg"
    real_image.write_bytes(b"real image data")

    # Change to tmp_path (simulating /home/user/code/)
    monkeypatch.chdir(tmp_path)

    # User provides path with project name prefix
    # First attempt: tmp_path/llm-image-analyzer/tests/data/image.jpg (doesn't exist)
    # Second attempt: tmp_path/tests/data/image.jpg (exists!)
    result = _resolve_path_with_fallback("llm-image-analyzer/tests/data/image.jpg")

    assert result.exists()
    assert result == real_image.resolve()
