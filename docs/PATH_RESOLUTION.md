# Path Resolution Strategy

## Overview

The LLM Image Analyzer MCP Server implements a two-step fallback strategy for resolving relative file paths. This helps handle cases where paths might be specified with or without the project root directory name.

## How It Works

When a relative path is provided to any tool that accepts image paths, the server attempts to resolve it using the following strategy:

### Step 1: Direct Resolution
First, the path is resolved relative to the current working directory (cwd).

**Example:**
- Current working directory: `/home/user/code/`
- Provided path: `someproject/picture.jpeg`
- First attempt: `/home/user/code/someproject/picture.jpeg`

If this path exists, it is used immediately.

### Step 2: Fallback with First Component Stripped
If the first attempt fails, the server strips the first directory component from the path and tries again.

**Example (continued):**
- Current working directory: `/home/user/code/`
- Provided path: `someproject/picture.jpeg`
- First attempt failed: `/home/user/code/someproject/picture.jpeg` (doesn't exist)
- Second attempt: `/home/user/code/picture.jpeg` (strips "someproject/")

This fallback helps when users accidentally include the project root directory name in their path.

## Use Cases

### Case 1: User Includes Project Directory
```python
# User working in /home/user/code/
# Image is at /home/user/code/images/photo.jpg

# User provides: "llm-image-analyzer/images/photo.jpg"
# First attempt: /home/user/code/llm-image-analyzer/images/photo.jpg ❌
# Second attempt: /home/user/code/images/photo.jpg ✓
```

### Case 2: User Provides Correct Relative Path
```python
# User working in /home/user/code/myproject/
# Image is at /home/user/code/myproject/assets/icon.png

# User provides: "assets/icon.png"
# First attempt: /home/user/code/myproject/assets/icon.png ✓
# (Second attempt not needed)
```

### Case 3: Deeply Nested Paths
```python
# User working in /home/user/code/
# Image is at /home/user/code/docs/images/screenshot.png

# User provides: "project/docs/images/screenshot.png"
# First attempt: /home/user/code/project/docs/images/screenshot.png ❌
# Second attempt: /home/user/code/docs/images/screenshot.png ✓
```

## Behavior Details

### Absolute Paths
Absolute paths are returned as-is without any fallback attempts:
```python
"/home/user/images/photo.jpg"  # Used directly
```

### Tilde Expansion
Tilde (`~`) is expanded to the user's home directory before resolution:
```python
"~/pictures/photo.jpg"  # Expands to /home/user/pictures/photo.jpg
```

### Single-Component Paths
Paths with only a filename (no directories) only attempt once:
```python
"photo.jpg"  # Only tries: /home/user/code/photo.jpg
```

### URLs
URLs are detected and handled separately (no path resolution):
```python
"https://example.com/image.jpg"  # Validated and used directly
```

### Symlinks
Symlinks are properly resolved to their target paths.

## Error Messages

When both resolution attempts fail, the error message shows both paths tried:

```
Image not found at path: someproject/image.jpg. 
Tried: /home/user/code/someproject/image.jpg and /home/user/code/image.jpg. 
Please check that the file exists and the path is correct.
```

For single-component paths, only one path is shown:
```
Image not found at path: image.jpg. 
Tried: /home/user/code/image.jpg. 
Please check that the file exists and the path is correct.
```

## Implementation

The fallback logic is implemented in the `_resolve_path_with_fallback()` function in `core.py`:

- Used by `_prepare_image_for_pydantic()` for PydanticAI-based analysis
- Used by `_analyze_with_mistral()` for Mistral Document AI processing
- Applies to all image path inputs across all tools

## Testing

Comprehensive tests are provided in `tests/test_path_resolution_fallback.py`, covering:

- Absolute path handling
- Relative path resolution (first attempt succeeds)
- Relative path fallback (second attempt succeeds)
- Nested path handling
- Error cases
- Edge cases (tilde expansion, symlinks, single-component paths)

Run tests with:
```bash
python3 -m pytest tests/test_path_resolution_fallback.py -v
```

## Related Tools

This path resolution strategy applies to:
- `analyze_images` tool (both PydanticAI and Mistral modes)
- Any future tools that accept image paths

## Design Rationale

This two-step approach provides a better user experience by:

1. **Forgiving user errors**: Users often include project directory names when copying paths from file explorers
2. **Maintaining compatibility**: Correct paths still work on the first attempt
3. **Minimal performance impact**: Only one extra filesystem check when needed
4. **Clear error messages**: Users see exactly which paths were attempted

## Configuration

No configuration needed - this behavior is automatic and always enabled.