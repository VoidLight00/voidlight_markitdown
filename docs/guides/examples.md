# VoidLight MarkItDown Examples

This guide provides practical examples for common use cases and advanced scenarios.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [File Format Examples](#file-format-examples)
3. [Korean Language Examples](#korean-language-examples)
4. [Batch Processing](#batch-processing)
5. [Web Integration](#web-integration)
6. [Error Handling](#error-handling)
7. [Advanced Scenarios](#advanced-scenarios)
8. [MCP Server Examples](#mcp-server-examples)

## Basic Examples

### Simple File Conversion

```python
from voidlight_markitdown import VoidLightMarkItDown

# Create converter
converter = VoidLightMarkItDown()

# Convert a PDF
result = converter.convert("report.pdf")
print(result.markdown)

# Save to file
with open("report.md", "w", encoding="utf-8") as f:
    f.write(result.markdown)
```

### Command Line Usage

```bash
# Basic conversion
voidlight-markitdown input.pdf -o output.md

# With Korean support
voidlight-markitdown --korean-mode document.docx -o output.md

# Multiple files
voidlight-markitdown *.pdf --output-dir markdown/

# From URL
voidlight-markitdown https://example.com/article.html -o article.md
```

### Accessing Metadata

```python
result = converter.convert("document.pdf")

# Access metadata
print(f"Title: {result.metadata.get('title', 'Untitled')}")
print(f"Author: {result.metadata.get('author', 'Unknown')}")
print(f"Pages: {result.metadata.get('page_count', 0)}")
print(f"Creation Date: {result.metadata.get('creation_date', 'N/A')}")

# Conversion statistics
print(f"Conversion Time: {result.conversion_time:.2f}s")
print(f"Character Count: {result.statistics.get('characters', 0)}")
print(f"Word Count: {result.statistics.get('words', 0)}")
```

## File Format Examples

### PDF with OCR

```python
# Scanned PDF with OCR
converter = VoidLightMarkItDown(
    config=Config(
        ocr_enabled=True,
        ocr_languages=["en", "ko"]
    )
)

result = converter.convert("scanned_document.pdf")

# Check if OCR was used
if result.metadata.get('ocr_performed'):
    print(f"OCR Confidence: {result.metadata.get('ocr_confidence', 0):.2%}")
```

### Excel with Multiple Sheets

```python
# Convert specific sheet
result = converter.convert(
    "data.xlsx",
    xlsx_options={"sheet_name": "Sales Data"}
)

# Convert all sheets
result = converter.convert(
    "workbook.xlsx",
    xlsx_options={
        "all_sheets": True,
        "sheet_separator": "\n\n# Sheet: {name}\n\n"
    }
)

# Access sheet data
for sheet in result.metadata.get('sheets', []):
    print(f"Sheet: {sheet['name']} - {sheet['rows']} rows")
```

### PowerPoint with Notes

```python
# Include speaker notes
result = converter.convert(
    "presentation.pptx",
    pptx_options={
        "include_notes": True,
        "extract_images": True,
        "slide_separator": "\n\n---\n\n"
    }
)

# Access slide information
slides = result.metadata.get('slides', [])
for i, slide in enumerate(slides):
    print(f"Slide {i+1}: {slide.get('title', 'Untitled')}")
    if slide.get('has_notes'):
        print("  - Has speaker notes")
```

### HTML Content Extraction

```python
# Extract main content from web page
result = converter.convert(
    "https://example.com/article.html",
    html_options={
        "extract_main_content": True,
        "remove_scripts": True,
        "remove_styles": True,
        "preserve_links": True
    }
)

# Clean blog post
result = converter.convert(
    "blog_post.html",
    html_options={
        "readability_mode": True,
        "include_images": True,
        "image_alt_text": True
    }
)
```

## Korean Language Examples

### Basic Korean Document

```python
# Enable Korean mode
converter = VoidLightMarkItDown(korean_mode=True)

# Convert Korean PDF
result = converter.convert("korean_document.pdf")

# Check Korean statistics
korean_stats = result.metadata.get('korean_stats', {})
print(f"Hangul Ratio: {korean_stats.get('hangul_ratio', 0):.2%}")
print(f"Contains Hanja: {korean_stats.get('has_hanja', False)}")
print(f"Mixed Script: {korean_stats.get('mixed_script', False)}")
```

### Korean Text Processing

```python
from voidlight_markitdown.korean import normalize_korean_text

# Configure Korean NLP
converter = VoidLightMarkItDown(
    korean_mode=True,
    config=Config(
        nlp_features={
            'tokenize': True,
            'pos_tagging': True,
            'extract_keywords': True
        }
    )
)

result = converter.convert("korean_article.docx")

# Access NLP results
tokens = result.metadata.get('korean_tokens', [])
keywords = result.metadata.get('keywords', [])
pos_tags = result.metadata.get('pos_tags', [])

print(f"Top Keywords: {', '.join(keywords[:5])}")
```

### Korean OCR

```python
# Korean image OCR
converter = VoidLightMarkItDown(
    korean_mode=True,
    config=Config(
        ocr_languages=['ko', 'en'],
        ocr_config={
            'korean_vertical_text': True,
            'mixed_script_mode': True
        }
    )
)

# Convert Korean signage image
result = converter.convert("korean_sign.jpg")

# OCR results
ocr_data = result.metadata.get('ocr_data', {})
print(f"Detected Scripts: {ocr_data.get('scripts', [])}")
print(f"Text Direction: {ocr_data.get('direction', 'horizontal')}")
```

### Mixed Language Documents

```python
# Handle Korean-English mixed documents
converter = VoidLightMarkItDown(
    korean_mode=True,
    config=Config(
        mixed_language_mode=True,
        preserve_language_tags=True
    )
)

result = converter.convert("bilingual_report.pdf")

# Language detection results
languages = result.metadata.get('detected_languages', [])
print(f"Languages: {', '.join(languages)}")

# Language-specific sections
sections = result.metadata.get('language_sections', [])
for section in sections:
    print(f"Section: {section['language']} - {section['percentage']:.1%}")
```

## Batch Processing

### Simple Batch Conversion

```python
from pathlib import Path

def batch_convert(input_dir: str, output_dir: str):
    """Convert all documents in a directory."""
    converter = VoidLightMarkItDown()
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for file in input_path.glob("*"):
        if file.is_file():
            try:
                print(f"Converting {file.name}...")
                result = converter.convert(file)
                
                # Save with same name but .md extension
                output_file = output_path / f"{file.stem}.md"
                output_file.write_text(result.markdown, encoding="utf-8")
                
                print(f"✓ Saved to {output_file}")
                
            except Exception as e:
                print(f"✗ Failed to convert {file.name}: {e}")

# Usage
batch_convert("documents/", "markdown/")
```

### Parallel Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple
import logging

def parallel_batch_convert(
    files: List[Path], 
    output_dir: Path,
    max_workers: int = 4
) -> List[Tuple[Path, bool]]:
    """Convert files in parallel."""
    converter = VoidLightMarkItDown()
    results = []
    
    def convert_file(file_path: Path) -> Tuple[Path, bool]:
        try:
            result = converter.convert(file_path)
            output_path = output_dir / f"{file_path.stem}.md"
            output_path.write_text(result.markdown, encoding="utf-8")
            return (file_path, True)
        except Exception as e:
            logging.error(f"Failed to convert {file_path}: {e}")
            return (file_path, False)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(convert_file, files))
    
    # Summary
    successful = sum(1 for _, success in results if success)
    print(f"Converted {successful}/{len(files)} files successfully")
    
    return results
```

### Filtered Batch Processing

```python
def convert_by_type(input_dir: Path, output_dir: Path, file_types: List[str]):
    """Convert only specific file types."""
    converter = VoidLightMarkItDown()
    
    # Filter files by type
    files = []
    for file_type in file_types:
        files.extend(input_dir.glob(f"**/*{file_type}"))
    
    print(f"Found {len(files)} files to convert")
    
    for file in files:
        # Maintain directory structure
        relative_path = file.relative_to(input_dir)
        output_path = output_dir / relative_path.with_suffix('.md')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            result = converter.convert(file)
            output_path.write_text(result.markdown, encoding="utf-8")
            print(f"✓ {relative_path}")
        except Exception as e:
            print(f"✗ {relative_path}: {e}")

# Convert only PDFs and Word documents
convert_by_type(
    Path("documents"),
    Path("markdown"),
    [".pdf", ".docx", ".doc"]
)
```

## Web Integration

### Flask API Example

```python
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile
import os

app = Flask(__name__)
converter = VoidLightMarkItDown()

@app.route('/convert', methods=['POST'])
def convert_document():
    """API endpoint for document conversion."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        file.save(tmp.name)
        
        try:
            # Convert options from request
            options = {
                'korean_mode': request.form.get('korean_mode', 'false').lower() == 'true',
                'ocr_enabled': request.form.get('ocr', 'false').lower() == 'true'
            }
            
            # Convert document
            result = converter.convert(tmp.name, **options)
            
            # Return as JSON or file
            if request.form.get('format') == 'json':
                return jsonify({
                    'markdown': result.markdown,
                    'metadata': result.metadata,
                    'statistics': result.statistics
                })
            else:
                # Return as markdown file
                output = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md')
                output.write(result.markdown)
                output.close()
                
                return send_file(
                    output.name,
                    as_attachment=True,
                    download_name=f"{secure_filename(file.filename)}.md",
                    mimetype='text/markdown'
                )
                
        finally:
            # Cleanup
            os.unlink(tmp.name)

@app.route('/convert/url', methods=['POST'])
def convert_url():
    """Convert document from URL."""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        result = converter.convert(url)
        return jsonify({
            'markdown': result.markdown,
            'metadata': result.metadata
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### FastAPI Example

```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os

app = FastAPI()
converter = VoidLightMarkItDown()

@app.post("/convert")
async def convert_document(
    file: UploadFile = File(...),
    korean_mode: bool = False,
    ocr_enabled: bool = False
):
    """Convert uploaded document to markdown."""
    # Save uploaded file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp.flush()
        
        try:
            # Convert
            result = converter.convert(
                tmp.name,
                korean_mode=korean_mode,
                ocr_enabled=ocr_enabled
            )
            
            return {
                "filename": file.filename,
                "markdown": result.markdown,
                "metadata": result.metadata,
                "statistics": result.statistics
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            os.unlink(tmp.name)

@app.post("/batch-convert")
async def batch_convert(files: List[UploadFile] = File(...)):
    """Convert multiple files."""
    results = []
    
    for file in files:
        try:
            # Process each file
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp.flush()
                
                result = converter.convert(tmp.name)
                results.append({
                    "filename": file.filename,
                    "success": True,
                    "markdown": result.markdown
                })
                
                os.unlink(tmp.name)
                
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    return {"results": results}
```

## Error Handling

### Comprehensive Error Handling

```python
from voidlight_markitdown import (
    VoidLightMarkItDown,
    UnsupportedFormatError,
    ConversionError,
    KoreanEncodingError,
    TimeoutError
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_convert(file_path: str) -> Optional[ConversionResult]:
    """Convert with comprehensive error handling."""
    converter = VoidLightMarkItDown()
    
    try:
        # Attempt conversion
        result = converter.convert(file_path)
        logger.info(f"Successfully converted {file_path}")
        return result
        
    except UnsupportedFormatError as e:
        logger.error(f"Unsupported format: {e}")
        # Could try alternative converter
        return None
        
    except KoreanEncodingError as e:
        logger.warning(f"Korean encoding issue: {e}")
        # Retry with Korean mode
        try:
            converter_kr = VoidLightMarkItDown(korean_mode=True)
            return converter_kr.convert(file_path, encoding='cp949')
        except Exception as e2:
            logger.error(f"Korean retry failed: {e2}")
            return None
            
    except TimeoutError as e:
        logger.error(f"Conversion timed out: {e}")
        # Could retry with longer timeout
        return None
        
    except ConversionError as e:
        logger.error(f"Conversion failed: {e}")
        # Log details for debugging
        logger.debug(f"File details: {Path(file_path).stat()}")
        return None
        
    except Exception as e:
        logger.exception(f"Unexpected error converting {file_path}")
        return None
```

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential
import time

class ResilientConverter:
    """Converter with retry logic."""
    
    def __init__(self):
        self.converter = VoidLightMarkItDown()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def convert_with_retry(self, file_path: str) -> ConversionResult:
        """Convert with automatic retry."""
        try:
            return self.converter.convert(file_path)
        except TimeoutError:
            # Increase timeout on retry
            self.converter.config.timeout *= 2
            raise
        except Exception as e:
            logger.warning(f"Conversion attempt failed: {e}")
            raise
    
    def convert_safe(self, file_path: str) -> Optional[ConversionResult]:
        """Safe conversion with fallbacks."""
        try:
            # Try with retry
            return self.convert_with_retry(file_path)
        except Exception as e:
            logger.error(f"All conversion attempts failed: {e}")
            
            # Try basic text extraction as fallback
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    text = content.decode('utf-8', errors='ignore')
                    return ConversionResult(
                        markdown=f"# Fallback Extraction\n\n{text}",
                        metadata={'fallback': True},
                        source_type='unknown'
                    )
            except:
                return None
```

## Advanced Scenarios

### Custom Converter Pipeline

```python
from typing import List, Callable

class ConversionPipeline:
    """Custom processing pipeline."""
    
    def __init__(self):
        self.converter = VoidLightMarkItDown()
        self.preprocessors: List[Callable] = []
        self.postprocessors: List[Callable] = []
    
    def add_preprocessor(self, func: Callable):
        """Add preprocessing step."""
        self.preprocessors.append(func)
    
    def add_postprocessor(self, func: Callable):
        """Add postprocessing step."""
        self.postprocessors.append(func)
    
    def convert(self, file_path: str) -> ConversionResult:
        """Convert with pipeline."""
        # Preprocess
        for preprocessor in self.preprocessors:
            file_path = preprocessor(file_path)
        
        # Convert
        result = self.converter.convert(file_path)
        
        # Postprocess
        for postprocessor in self.postprocessors:
            result = postprocessor(result)
        
        return result

# Example usage
pipeline = ConversionPipeline()

# Add header to all documents
def add_header(result: ConversionResult) -> ConversionResult:
    header = f"# Converted Document\n\nGenerated: {datetime.now()}\n\n---\n\n"
    result.markdown = header + result.markdown
    return result

# Clean up formatting
def clean_formatting(result: ConversionResult) -> ConversionResult:
    # Remove multiple blank lines
    import re
    result.markdown = re.sub(r'\n{3,}', '\n\n', result.markdown)
    return result

pipeline.add_postprocessor(add_header)
pipeline.add_postprocessor(clean_formatting)

result = pipeline.convert("document.pdf")
```

### Stream Processing Large Files

```python
def process_large_file_stream(file_path: str, output_path: str):
    """Process large file with streaming."""
    converter = VoidLightMarkItDown(stream_mode=True)
    
    bytes_processed = 0
    chunks_written = 0
    
    with open(output_path, 'w', encoding='utf-8') as output:
        # Process in chunks
        with converter.convert_stream(file_path) as stream:
            for chunk in stream:
                # Write chunk
                output.write(chunk.content)
                chunks_written += 1
                bytes_processed += len(chunk.content.encode('utf-8'))
                
                # Progress update
                if chunks_written % 10 == 0:
                    print(f"Processed {chunks_written} chunks, "
                          f"{bytes_processed / 1024 / 1024:.2f} MB")
                
                # Could process chunk here (indexing, analysis, etc.)
                process_chunk(chunk)
    
    print(f"Completed: {chunks_written} chunks, "
          f"{bytes_processed / 1024 / 1024:.2f} MB total")

def process_chunk(chunk: MarkdownChunk):
    """Process individual chunk."""
    # Example: Extract headings for TOC
    import re
    headings = re.findall(r'^#{1,6}\s+(.+)$', chunk.content, re.MULTILINE)
    for heading in headings:
        print(f"Found heading: {heading}")
```

### Integration with LLMs

```python
import openai

class LLMEnhancedConverter:
    """Converter with LLM enhancement."""
    
    def __init__(self, api_key: str):
        self.converter = VoidLightMarkItDown()
        openai.api_key = api_key
    
    def convert_with_summary(self, file_path: str) -> dict:
        """Convert and generate AI summary."""
        # Convert document
        result = self.converter.convert(file_path)
        
        # Generate summary using LLM
        summary_prompt = f"""
        Please provide a concise summary of this document:
        
        {result.markdown[:3000]}  # First 3000 chars
        
        Summary:
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=200
        )
        
        summary = response.choices[0].message.content
        
        return {
            "markdown": result.markdown,
            "summary": summary,
            "metadata": result.metadata,
            "key_points": self.extract_key_points(result.markdown)
        }
    
    def extract_key_points(self, markdown: str) -> List[str]:
        """Extract key points using LLM."""
        # Implementation
        pass
```

## MCP Server Examples

### Basic MCP Usage

```python
# Start MCP server
import subprocess

# STDIO mode
mcp_process = subprocess.Popen(
    ["voidlight-markitdown-mcp"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Send request
import json

request = {
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/call",
    "params": {
        "name": "convert_document",
        "arguments": {
            "source": "document.pdf",
            "korean_mode": True
        }
    }
}

mcp_process.stdin.write(json.dumps(request) + "\n")
mcp_process.stdin.flush()

# Read response
response_line = mcp_process.stdout.readline()
response = json.loads(response_line)
print(response["result"]["content"][0]["text"])
```

### HTTP MCP Client

```python
import httpx
import asyncio

class MCPHTTPClient:
    """HTTP client for MCP server."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def convert(self, file_path: str, **options):
        """Convert document via HTTP."""
        response = await self.client.post(
            f"{self.base_url}/convert",
            json={
                "source": file_path,
                **options
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def convert_stream(self, file_path: str):
        """Stream conversion via SSE."""
        async with self.client.stream(
            'GET',
            f"{self.base_url}/sse",
            params={"source": file_path}
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    yield data

# Usage
async def main():
    client = MCPHTTPClient()
    
    # Simple conversion
    result = await client.convert("document.pdf", korean_mode=True)
    print(result["markdown"])
    
    # Streaming
    async for chunk in client.convert_stream("large.pdf"):
        print(f"Chunk {chunk['index']}: {len(chunk['content'])} chars")

asyncio.run(main())
```

---

<div align="center">
  <p>For more details, see the <a href="../api/python-api.md">API Reference</a></p>
  <p><a href="../">Back to Documentation Home</a></p>
</div>