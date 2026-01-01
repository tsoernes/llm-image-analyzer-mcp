# Example Usage

This document shows common usage patterns for the LLM Image Analyzer MCP Server.

## Example 1: Compare Two Screenshots

Compare two versions of a UI to identify changes:

```json
{
  "prompt": "What are the visual differences between these two screenshots? List all UI changes you can identify.",
  "image_paths": [
    "/home/user/screenshots/before.png",
    "/home/user/screenshots/after.png"
  ],
  "detail": "high",
  "reasoning_effort": "high"
}
```

**Expected Response:**
```json
{
  "analysis": "The screenshots show several UI changes:\n1. The header color changed from blue to green\n2. A new 'Settings' button was added in the top right...",
  "model": "gpt-5.2",
  "prompt_tokens": 1250,
  "completion_tokens": 450,
  "total_tokens": 1700
}
```

## Example 2: Describe an Image from URL

Get a detailed description of an image hosted online:

```json
{
  "prompt": "Provide a detailed description of this image, including colors, objects, composition, and mood.",
  "image_paths": ["https://example.com/photo.jpg"],
  "detail": "high"
}
```

## Example 3: Extract Text (OCR)

Extract text from a document or screenshot:

```json
{
  "prompt": "Extract all visible text from this document, maintaining the original structure and formatting as much as possible.",
  "image_paths": ["~/documents/receipt.png"],
  "max_tokens": 1000,
  "detail": "high"
}
```

## Example 4: Identify Objects

Identify and count objects in an image:

```json
{
  "prompt": "Count how many people are visible in this image and describe what they are doing.",
  "image_paths": ["/path/to/group-photo.jpg"]
}
```

## Example 5: Analyze Multiple Images

Analyze a sequence of images:

```json
{
  "prompt": "These are three frames from a video sequence. Describe what is happening across these frames and identify any motion or changes.",
  "image_paths": [
    "https://example.com/frame1.jpg",
    "https://example.com/frame2.jpg",
    "https://example.com/frame3.jpg"
  ],
  "detail": "auto"
}
```

## Example 6: Logo/Brand Identification

Identify brands or logos in an image:

```json
{
  "prompt": "What brands or logos are visible in this image? List each one you can identify.",
  "image_paths": ["~/photos/storefront.jpg"],
  "reasoning_effort": "medium"
}
```

## Example 7: Diagram Analysis

Analyze technical diagrams or charts:

```json
{
  "prompt": "Explain what this diagram shows. What is the main concept being illustrated?",
  "image_paths": ["https://example.com/architecture-diagram.png"],
  "detail": "high",
  "max_tokens": 800
}
```

## Example 8: Quick Analysis (Low Detail)

Fast, low-cost analysis for simple images:

```json
{
  "prompt": "Is this image suitable for a professional website banner?",
  "image_paths": ["/path/to/banner-candidate.jpg"],
  "detail": "low",
  "reasoning_effort": "low",
  "max_tokens": 200
}
```

## Example 9: Using Custom Model

Use a specific model deployment:

```json
{
  "prompt": "Describe the technical components visible in this circuit board photo.",
  "image_paths": ["~/electronics/pcb-photo.jpg"],
  "model": "gpt-4o",
  "detail": "high"
}
```

## Example 10: Error Handling

Invalid image path triggers helpful error:

```json
{
  "prompt": "Describe this image",
  "image_paths": ["/nonexistent/image.jpg"]
}
```

**Response:**
```json
{
  "error": "Image not found at path: /nonexistent/image.jpg. Please check that the file exists and the path is correct.",
  "error_type": "FileNotFoundError",
  "debug_mode": false
}
```

## Testing with MCP Inspector

To test the server interactively:

```bash
# Start MCP Inspector
npx @modelcontextprotocol/inspector uv run llm-image-analyzer-mcp

# Or use the installed command
npx @modelcontextprotocol/inspector uv run python -m llm_image_analyzer_mcp.server
```

Then in the web interface:
1. Select the `analyze_images` tool
2. Fill in the parameters
3. Click "Run Tool"
4. View the results

## Debug Mode Examples

Enable debug mode for detailed error traces:

```bash
export MCP_DEBUG=true
uv run llm-image-analyzer-mcp
```

When an error occurs, you'll get full stack traces:

```json
{
  "error": "Invalid image file at bad-file.txt. Supported formats: JPEG, PNG, GIF, WebP. Error: cannot identify image file",
  "error_type": "ValueError",
  "debug_mode": true,
  "traceback": "Traceback (most recent call last):\n  File \"/path/to/server.py\", line 98, in _encode_image_from_path\n    with Image.open(path) as img:\n..."
}
```

## Performance Tips

1. **Use `detail="low"`** for simple images or when speed/cost matters
2. **Set `max_tokens`** to limit response length for concise analysis
3. **Use `reasoning_effort="low"`** for quick, straightforward tasks
4. **Batch related images** in a single call when comparing or analyzing sequences
5. **Use URLs** when possible to avoid base64 encoding overhead