# VoidLight MarkItDown

Enhanced document-to-markdown conversion library with superior Korean language support.

한국어 지원이 강화된 문서-마크다운 변환 라이브러리입니다.

## Overview / 개요

VoidLight MarkItDown is a fork of the original MarkItDown project with significant enhancements for Korean language processing. It provides both a Python library and an MCP (Model Context Protocol) server for converting various document formats to Markdown.

VoidLight MarkItDown은 한국어 처리 기능이 대폭 강화된 MarkItDown 프로젝트의 포크입니다. 다양한 문서 형식을 마크다운으로 변환하는 Python 라이브러리와 MCP (Model Context Protocol) 서버를 제공합니다.

## Key Features / 주요 기능

- 🇰🇷 **Enhanced Korean Support** / 강화된 한국어 지원
  - Smart encoding detection for Korean documents / 한국어 문서의 스마트 인코딩 감지
  - Korean text normalization / 한국어 텍스트 정규화
  - Mixed script support (Korean, Chinese, English) / 다중 문자 지원 (한국어, 한자, 영어)
  - Optimized for Korean PDF and DOCX files / 한국어 PDF 및 DOCX 파일 최적화

- 📄 **Wide Format Support** / 다양한 형식 지원
  - Documents: PDF, DOCX, PPTX, XLSX, CSV
  - Web: HTML, RSS, Wikipedia
  - Media: Images (OCR), Audio (transcription)
  - Data: JSON, XML, Jupyter Notebooks
  - Archives: ZIP, EPUB

- 🤖 **LLM Optimized** / LLM 최적화
  - Clean, structured Markdown output / 깔끔하고 구조화된 마크다운 출력
  - Metadata preservation / 메타데이터 보존
  - MCP server for AI integration / AI 통합을 위한 MCP 서버

## Project Structure / 프로젝트 구조

```
voidlight_markitdown/
├── packages/
│   ├── voidlight_markitdown/       # Main Python library / 메인 Python 라이브러리
│   └── voidlight_markitdown-mcp/   # MCP server / MCP 서버
└── README.md
```

## Quick Start / 빠른 시작

### Library Installation / 라이브러리 설치

```bash
# Basic installation / 기본 설치
pip install voidlight-markitdown

# With all features / 모든 기능 포함
pip install voidlight-markitdown[all]

# With Korean support / 한국어 지원 포함
pip install voidlight-markitdown[korean]
```

### MCP Server Installation / MCP 서버 설치

```bash
pip install voidlight-markitdown-mcp
```

## Usage Examples / 사용 예제

### Python Library / Python 라이브러리

```python
from voidlight_markitdown import VoidLightMarkItDown

# Standard usage / 표준 사용법
converter = VoidLightMarkItDown()
result = converter.convert("document.pdf")
print(result.markdown)

# Korean mode / 한국어 모드
converter = VoidLightMarkItDown(korean_mode=True)
result = converter.convert("korean_document.docx")
print(result.markdown)
```

### Command Line / 명령줄

```bash
# Convert a file / 파일 변환
voidlight-markitdown input.pdf -o output.md

# Korean mode / 한국어 모드
voidlight-markitdown --korean-mode korean.pdf -o output.md
```

### MCP Server / MCP 서버

```bash
# Run MCP server (STDIO) / MCP 서버 실행 (STDIO)
voidlight-markitdown-mcp

# Run with HTTP/SSE / HTTP/SSE로 실행
voidlight-markitdown-mcp --http --port 3001
```

## Documentation / 문서

- [VoidLight MarkItDown Library Documentation](packages/voidlight_markitdown/README.md)
- [VoidLight MarkItDown MCP Server Documentation](packages/voidlight_markitdown-mcp/README.md)

## Development / 개발

### Setup / 설정

```bash
# Clone the repository / 저장소 복제
git clone https://github.com/voidlight/voidlight_markitdown.git
cd voidlight_markitdown

# Install in development mode / 개발 모드로 설치
pip install -e packages/voidlight_markitdown[dev]
pip install -e packages/voidlight_markitdown-mcp
```

### Testing / 테스트

```bash
# Run tests / 테스트 실행
cd packages/voidlight_markitdown
pytest

cd ../voidlight_markitdown-mcp
pytest
```

## License / 라이선스

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

이 프로젝트는 MIT 라이선스에 따라 라이선스가 부여됩니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## Credits / 크레딧

This project is based on the original [MarkItDown](https://github.com/microsoft/markitdown) project by Microsoft, with enhancements for Korean language support by VoidLight.

이 프로젝트는 Microsoft의 원본 [MarkItDown](https://github.com/microsoft/markitdown) 프로젝트를 기반으로 하며, VoidLight가 한국어 지원을 강화했습니다.

## Contributing / 기여

Contributions are welcome! Please feel free to submit a Pull Request.

기여를 환영합니다! 자유롭게 Pull Request를 제출해 주세요.