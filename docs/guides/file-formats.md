# Supported File Formats Guide

VoidLight MarkItDown supports a wide range of file formats, each with specific features and optimizations. This guide provides detailed information about each supported format.

## Table of Contents

1. [Document Formats](#document-formats)
   - [PDF (.pdf)](#pdf-pdf)
   - [Microsoft Word (.docx)](#microsoft-word-docx)
   - [Microsoft Excel (.xlsx, .xls)](#microsoft-excel-xlsx-xls)
   - [Microsoft PowerPoint (.pptx)](#microsoft-powerpoint-pptx)
2. [Text Formats](#text-formats)
   - [Plain Text (.txt)](#plain-text-txt)
   - [Markdown (.md)](#markdown-md)
   - [CSV (.csv)](#csv-csv)
3. [Web Formats](#web-formats)
   - [HTML (.html, .htm)](#html-html-htm)
   - [XML (.xml)](#xml-xml)
   - [RSS (.rss, .atom)](#rss-rss-atom)
4. [Data Formats](#data-formats)
   - [JSON (.json)](#json-json)
   - [Jupyter Notebooks (.ipynb)](#jupyter-notebooks-ipynb)
5. [Image Formats](#image-formats)
   - [Common Images](#common-images)
6. [Archive Formats](#archive-formats)
   - [ZIP (.zip)](#zip-zip)
   - [EPUB (.epub)](#epub-epub)
7. [Audio Formats](#audio-formats)
8. [Special Sources](#special-sources)

## Document Formats

### PDF (.pdf)

PDF is one of the most common document formats with comprehensive support.

#### Features
- Text extraction with layout preservation
- Table detection and conversion
- Image extraction
- OCR for scanned documents
- Metadata extraction
- Korean text support

#### Usage
```python
from voidlight_markitdown import VoidLightMarkItDown

converter = VoidLightMarkItDown()
result = converter.convert("document.pdf")

# With OCR for scanned PDFs
result = converter.convert("scanned.pdf", ocr_enabled=True)

# Korean PDF
converter_kr = VoidLightMarkItDown(korean_mode=True)
result = converter_kr.convert("korean.pdf")
```

#### Options
```python
result = converter.convert("document.pdf", 
    pdf_options={
        "extract_images": True,      # Extract embedded images
        "preserve_layout": True,     # Maintain layout structure
        "ocr_language": "eng+kor",  # OCR languages
        "page_range": "1-10",       # Specific pages
        "password": "secret"        # For encrypted PDFs
    }
)
```

#### Best Practices
- Enable OCR for scanned documents
- Use Korean mode for Korean PDFs
- Extract images separately if needed
- Handle password-protected PDFs

### Microsoft Word (.docx)

Modern Word documents with rich formatting support.

#### Features
- Style preservation
- Table conversion
- Image extraction
- Comment extraction
- Track changes support
- Header/footer handling
- Korean text support

#### Usage
```python
result = converter.convert("document.docx")

# With style preservation
result = converter.convert("styled.docx",
    docx_options={
        "preserve_styles": True,
        "extract_comments": True,
        "include_headers": True
    }
)
```

#### Table Handling
```python
# Tables are converted to Markdown tables
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
```

#### Best Practices
- Use style preservation for formatted documents
- Extract comments for review documents
- Handle embedded objects appropriately

### Microsoft Excel (.xlsx, .xls)

Spreadsheet conversion with table support.

#### Features
- Multiple sheet support
- Formula results
- Cell formatting
- Merged cell handling
- Chart descriptions
- Korean text in cells

#### Usage
```python
result = converter.convert("spreadsheet.xlsx")

# Specific sheet
result = converter.convert("data.xlsx",
    xlsx_options={
        "sheet_name": "Sheet2",
        "include_formulas": True,
        "date_format": "%Y-%m-%d"
    }
)

# All sheets
result = converter.convert("workbook.xlsx",
    xlsx_options={
        "all_sheets": True,
        "sheet_separator": "\n---\n"
    }
)
```

#### Output Format
```markdown
## Sheet: Sales Data

| Product | Q1 | Q2 | Q3 | Q4 | Total |
|---------|----|----|----|----|-------|
| Item A  | 100| 150| 200| 180| 630   |
| Item B  | 80 | 90 | 110| 120| 400   |
```

### Microsoft PowerPoint (.pptx)

Presentation conversion with slide structure.

#### Features
- Slide-by-slide conversion
- Text extraction
- Image descriptions
- Speaker notes
- Layout preservation
- Animation descriptions

#### Usage
```python
result = converter.convert("presentation.pptx")

# With speaker notes
result = converter.convert("slides.pptx",
    pptx_options={
        "include_notes": True,
        "slide_separator": "\n\n---\n\n",
        "extract_images": True
    }
)
```

#### Output Format
```markdown
# Slide 1: Title Slide

## Main Title
Subtitle text

---

# Slide 2: Content

- Bullet point 1
- Bullet point 2
  - Sub-bullet

Speaker Notes: Remember to emphasize this point
```

## Text Formats

### Plain Text (.txt)

Simple text file conversion with encoding detection.

#### Features
- Automatic encoding detection
- Korean encoding support (UTF-8, CP949, EUC-KR)
- Line ending normalization
- Character set conversion

#### Usage
```python
# Auto-detect encoding
result = converter.convert("text.txt")

# Specify encoding
result = converter.convert("korean.txt", encoding="cp949")

# With preprocessing
result = converter.convert("messy.txt",
    txt_options={
        "normalize_whitespace": True,
        "fix_encoding": True
    }
)
```

### Markdown (.md)

Markdown files are processed and normalized.

#### Features
- Syntax validation
- Link checking
- Image path resolution
- Code block formatting
- Table normalization

#### Usage
```python
result = converter.convert("document.md",
    md_options={
        "validate_links": True,
        "fix_syntax": True,
        "resolve_images": True
    }
)
```

### CSV (.csv)

Comma-separated values conversion to tables.

#### Features
- Automatic delimiter detection
- Header detection
- Encoding support
- Large file handling
- Korean text support

#### Usage
```python
# Basic conversion
result = converter.convert("data.csv")

# Custom delimiter
result = converter.convert("data.tsv",
    csv_options={
        "delimiter": "\t",
        "has_header": True,
        "encoding": "utf-8"
    }
)

# Korean CSV
result = converter.convert("korean_data.csv",
    encoding="cp949",
    korean_mode=True
)
```

## Web Formats

### HTML (.html, .htm)

Web page conversion with content extraction.

#### Features
- Clean content extraction
- Link preservation
- Image handling
- CSS style interpretation
- JavaScript content handling
- Meta tag extraction

#### Usage
```python
# Local HTML file
result = converter.convert("page.html")

# From URL
result = converter.convert("https://example.com")

# With options
result = converter.convert("article.html",
    html_options={
        "extract_main_content": True,
        "remove_scripts": True,
        "preserve_links": True,
        "include_meta": True
    }
)
```

#### Main Content Extraction
```python
# Automatically extracts article content
result = converter.convert("blog_post.html",
    html_options={
        "readability_mode": True
    }
)
```

### XML (.xml)

Structured XML conversion.

#### Features
- Schema validation
- XPath support
- Namespace handling
- XSLT transformation

#### Usage
```python
result = converter.convert("data.xml",
    xml_options={
        "pretty_print": True,
        "include_attributes": True,
        "xpath_filter": "//article"
    }
)
```

### RSS (.rss, .atom)

RSS/Atom feed conversion.

#### Features
- Feed parsing
- Entry extraction
- Date formatting
- Content cleaning

#### Usage
```python
result = converter.convert("feed.rss",
    rss_options={
        "entries_limit": 10,
        "include_dates": True,
        "clean_html": True
    }
)
```

## Data Formats

### JSON (.json)

JSON file pretty printing and conversion.

#### Features
- Pretty formatting
- Schema validation
- Path extraction
- Table conversion for arrays

#### Usage
```python
# Basic conversion
result = converter.convert("data.json")

# With formatting
result = converter.convert("api_response.json",
    json_options={
        "indent": 2,
        "sort_keys": True,
        "extract_tables": True
    }
)
```

#### Array to Table Conversion
```python
# JSON arrays can be converted to tables
[
  {"name": "John", "age": 30},
  {"name": "Jane", "age": 25}
]

# Becomes:
| name | age |
|------|-----|
| John | 30  |
| Jane | 25  |
```

### Jupyter Notebooks (.ipynb)

Notebook conversion with code and output.

#### Features
- Code cell extraction
- Output preservation
- Markdown cell formatting
- Image output handling
- Execution order

#### Usage
```python
result = converter.convert("notebook.ipynb",
    ipynb_options={
        "include_outputs": True,
        "include_source": True,
        "clear_outputs": False,
        "language_hints": True
    }
)
```

#### Output Format
```markdown
## Cell 1 (Code)
```python
import pandas as pd
df = pd.read_csv('data.csv')
print(df.head())
```

### Output:
```
   Column1  Column2
0       1        A
1       2        B
```
```

## Image Formats

### Common Images

Supports JPEG, PNG, GIF, BMP, TIFF, WebP with OCR.

#### Features
- OCR text extraction
- EXIF data reading
- Korean text OCR
- Multi-language OCR
- Image description

#### Usage
```python
# Basic OCR
result = converter.convert("screenshot.png")

# Korean OCR
result = converter.convert("korean_image.jpg",
    korean_mode=True,
    image_options={
        "ocr_languages": ["ko", "en"],
        "extract_text_regions": True,
        "confidence_threshold": 0.8
    }
)

# With preprocessing
result = converter.convert("scan.tiff",
    image_options={
        "preprocess": {
            "deskew": True,
            "denoise": True,
            "enhance": True
        }
    }
)
```

#### OCR Languages
- English: `en`
- Korean: `ko`
- Chinese: `zh`
- Japanese: `ja`
- Many more supported

## Archive Formats

### ZIP (.zip)

Archive extraction and content conversion.

#### Features
- Recursive extraction
- File filtering
- Password support
- Nested archive handling

#### Usage
```python
# Extract and convert all files
result = converter.convert("archive.zip")

# With filtering
result = converter.convert("docs.zip",
    zip_options={
        "file_filter": "*.pdf",
        "recursive": True,
        "password": "secret"
    }
)
```

### EPUB (.epub)

E-book conversion with chapter structure.

#### Features
- Chapter extraction
- TOC preservation
- Image handling
- Metadata extraction
- Style preservation

#### Usage
```python
result = converter.convert("book.epub",
    epub_options={
        "include_toc": True,
        "chapter_separator": "\n# ",
        "extract_cover": True
    }
)
```

## Audio Formats

### Supported Formats

MP3, WAV, M4A, FLAC, OGG - with transcription support.

#### Features
- Speech-to-text transcription
- Multiple language support
- Timestamp inclusion
- Speaker detection

#### Usage
```python
# Basic transcription
result = converter.convert("audio.mp3")

# With options
result = converter.convert("interview.wav",
    audio_options={
        "language": "ko",
        "include_timestamps": True,
        "speaker_detection": True,
        "model": "large"
    }
)
```

## Special Sources

### URLs

Direct web page conversion.

```python
# Web page
result = converter.convert("https://example.com/article")

# With options
result = converter.convert("https://example.com",
    url_options={
        "wait_for_js": True,
        "timeout": 30,
        "user_agent": "custom"
    }
)
```

### Wikipedia

Special Wikipedia article handling.

```python
# Wikipedia URL
result = converter.convert("https://en.wikipedia.org/wiki/Python")

# Korean Wikipedia
result = converter.convert("https://ko.wikipedia.org/wiki/파이썬",
    korean_mode=True
)
```

### YouTube

Video transcript extraction.

```python
# YouTube video
result = converter.convert("https://youtube.com/watch?v=...")

# With options
result = converter.convert("https://youtube.com/watch?v=...",
    youtube_options={
        "include_captions": True,
        "language": "ko",
        "include_timestamps": True
    }
)
```

## Format Detection

VoidLight MarkItDown automatically detects file formats based on:

1. **File Extension** - Primary detection method
2. **MIME Type** - For web content
3. **Magic Bytes** - File signature detection
4. **Content Analysis** - For ambiguous cases

```python
from voidlight_markitdown.utils import detect_format

# Detect format
format_info = detect_format("mystery_file")
print(f"Format: {format_info.format}")
print(f"Confidence: {format_info.confidence}")
```

## Best Practices by Format

### Documents (PDF, DOCX, PPTX)
- Enable OCR for scanned content
- Use Korean mode for Korean documents
- Extract images when needed
- Handle passwords securely

### Spreadsheets (XLSX, CSV)
- Check for multiple sheets
- Preserve formulas when relevant
- Handle date formats correctly
- Consider memory for large files

### Web Content (HTML, XML)
- Extract main content only
- Handle encoding properly
- Validate links if needed
- Remove unnecessary scripts

### Images
- Use appropriate OCR languages
- Preprocess for better results
- Set confidence thresholds
- Handle multi-page TIFFs

### Archives
- Filter unnecessary files
- Handle nested archives
- Use streaming for large files
- Manage temporary files

---

<div align="center">
  <p>For format-specific examples, see the <a href="examples.md">Examples Guide</a></p>
  <p><a href="../">Back to Documentation Home</a></p>
</div>