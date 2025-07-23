# Getting Started with VoidLight MarkItDown

This guide will help you get up and running with VoidLight MarkItDown quickly.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Basic Usage](#basic-usage)
5. [Next Steps](#next-steps)

## Prerequisites

Before installing VoidLight MarkItDown, ensure you have:

- **Python 3.9 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** - Python package installer (comes with Python)
- **Git** (optional) - For cloning the repository

### System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM (8GB recommended for large files)
- **Disk Space**: 500MB for installation + space for document processing

## Installation

### Method 1: Install from PyPI (Recommended)

```bash
# Basic installation
pip install voidlight-markitdown

# With all features
pip install voidlight-markitdown[all]

# With Korean language support
pip install voidlight-markitdown[korean]

# With MCP server
pip install voidlight-markitdown-mcp
```

### Method 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/VoidLight00/voidlight_markitdown.git
cd voidlight_markitdown

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e packages/voidlight_markitdown[all]
pip install -e packages/voidlight_markitdown-mcp
```

### Verify Installation

```bash
# Check CLI installation
voidlight-markitdown --version

# Check Python import
python -c "import voidlight_markitdown; print(voidlight_markitdown.__version__)"
```

## Quick Start

### Convert Your First Document

#### Using Command Line

```bash
# Convert a PDF to Markdown
voidlight-markitdown document.pdf -o output.md

# Convert with Korean mode enabled
voidlight-markitdown --korean-mode korean_doc.docx -o korean_output.md

# Convert and display in terminal
voidlight-markitdown presentation.pptx
```

#### Using Python

```python
from voidlight_markitdown import VoidLightMarkItDown

# Create converter instance
converter = VoidLightMarkItDown()

# Convert a document
result = converter.convert("document.pdf")
print(result.markdown)

# Save to file
with open("output.md", "w", encoding="utf-8") as f:
    f.write(result.markdown)
```

### Start MCP Server

```bash
# Start in STDIO mode (for Claude Desktop)
voidlight-markitdown-mcp

# Start in HTTP mode
voidlight-markitdown-mcp --mode http --port 8080
```

## Basic Usage

### Converting Different File Types

```python
from voidlight_markitdown import VoidLightMarkItDown

converter = VoidLightMarkItDown()

# PDF conversion
pdf_result = converter.convert("report.pdf")

# Word document
docx_result = converter.convert("document.docx")

# Excel spreadsheet
xlsx_result = converter.convert("data.xlsx")

# PowerPoint presentation
pptx_result = converter.convert("slides.pptx")

# Web page
html_result = converter.convert("https://example.com")

# Image with OCR
image_result = converter.convert("screenshot.png")
```

### Korean Mode

```python
# Enable Korean processing
converter = VoidLightMarkItDown(korean_mode=True)

# Convert Korean document
result = converter.convert("korean_document.pdf")

# The converter will automatically:
# - Detect Korean encoding (UTF-8, CP949, EUC-KR)
# - Normalize Korean text
# - Handle mixed scripts (Korean, Chinese, English)
# - Apply Korean-specific OCR for images
```

### Handling Results

```python
result = converter.convert("document.pdf")

# Access markdown content
markdown_content = result.markdown

# Access metadata
metadata = result.metadata
print(f"Title: {metadata.get('title', 'N/A')}")
print(f"Pages: {metadata.get('page_count', 'N/A')}")

# Check for errors
if result.errors:
    for error in result.errors:
        print(f"Warning: {error}")
```

### Stream Processing (Large Files)

```python
# Enable streaming for large files
converter = VoidLightMarkItDown(stream_mode=True)

# Process in chunks
with converter.convert_stream("large_file.pdf") as stream:
    for chunk in stream:
        process_chunk(chunk)  # Your processing logic
```

## Configuration Options

### Environment Variables

```bash
# Set default Korean mode
export VOIDLIGHT_KOREAN_MODE=true

# Set logging level
export VOIDLIGHT_LOG_LEVEL=INFO

# Set temp directory
export VOIDLIGHT_TEMP_DIR=/path/to/temp
```

### Python Configuration

```python
from voidlight_markitdown import VoidLightMarkItDown, Config

# Custom configuration
config = Config(
    korean_mode=True,
    ocr_enabled=True,
    max_file_size=100 * 1024 * 1024,  # 100MB
    timeout=300,  # 5 minutes
    temp_dir="/custom/temp"
)

converter = VoidLightMarkItDown(config=config)
```

## Common Use Cases

### Batch Processing

```python
import os
from pathlib import Path
from voidlight_markitdown import VoidLightMarkItDown

converter = VoidLightMarkItDown()
input_dir = Path("documents")
output_dir = Path("markdown")
output_dir.mkdir(exist_ok=True)

for file_path in input_dir.glob("*"):
    if file_path.is_file():
        try:
            result = converter.convert(str(file_path))
            output_path = output_dir / f"{file_path.stem}.md"
            output_path.write_text(result.markdown, encoding="utf-8")
            print(f"✓ Converted: {file_path.name}")
        except Exception as e:
            print(f"✗ Failed: {file_path.name} - {e}")
```

### API Integration

```python
from flask import Flask, request, jsonify
from voidlight_markitdown import VoidLightMarkItDown

app = Flask(__name__)
converter = VoidLightMarkItDown()

@app.route('/convert', methods=['POST'])
def convert_document():
    file = request.files['document']
    result = converter.convert_file(file)
    return jsonify({
        'markdown': result.markdown,
        'metadata': result.metadata
    })
```

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure you've activated your virtual environment
2. **Missing Dependencies**: Run `pip install voidlight-markitdown[all]`
3. **Korean Text Issues**: Install Korean support with `pip install voidlight-markitdown[korean]`
4. **Permission Errors**: Check file permissions and temp directory access

### Getting Help

- Check the [FAQ](faq.md)
- Read the [Troubleshooting Guide](troubleshooting.md)
- Search [GitHub Issues](https://github.com/VoidLight00/voidlight_markitdown/issues)
- Ask in [Discussions](https://github.com/VoidLight00/voidlight_markitdown/discussions)

## Next Steps

Now that you've got VoidLight MarkItDown running:

1. 📖 Read the [Basic Usage Guide](basic-usage.md) for more examples
2. 🇰🇷 Explore [Korean Language Features](korean-features.md)
3. 📄 Learn about [Supported File Formats](file-formats.md)
4. 🤖 Set up the [MCP Server](mcp-server.md) for AI integration
5. 🚀 Check out [Advanced Features](advanced-features.md)

---

<div align="center">
  <p>Happy converting! 🎉</p>
  <p><a href="../">Back to Documentation Home</a></p>
</div>