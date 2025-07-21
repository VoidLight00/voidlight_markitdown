# VoidLight MarkItDown

[![PyPI](https://img.shields.io/pypi/v/voidlight-markitdown.svg)](https://pypi.org/project/voidlight-markitdown/)
[![Python Versions](https://img.shields.io/pypi/pyversions/voidlight-markitdown.svg)](https://pypi.org/project/voidlight-markitdown/)

VoidLight MarkItDown is an enhanced version of MarkItDown with superior Korean language support. It's a Python library for converting various document formats to Markdown, optimized for LLM usage.

VoidLight MarkItDown은 뛰어난 한국어 지원을 제공하는 MarkItDown의 강화 버전입니다. 다양한 문서 형식을 마크다운으로 변환하는 Python 라이브러리로, LLM 사용에 최적화되어 있습니다.

## Features / 기능

### Core Features / 핵심 기능
- Convert various file formats to Markdown / 다양한 파일 형식을 마크다운으로 변환
- Support for text, images, audio, and structured data / 텍스트, 이미지, 오디오 및 구조화된 데이터 지원
- Extensible plugin architecture / 확장 가능한 플러그인 아키텍처
- LLM-optimized output / LLM 최적화 출력

### Enhanced Korean Support / 강화된 한국어 지원
- **Smart Korean encoding detection** / 스마트 한국어 인코딩 감지
- **Korean text normalization** / 한국어 텍스트 정규화
- **Mixed Korean-Chinese text support** / 한국어-한자 혼용 텍스트 지원
- **Optimized line break handling** / 최적화된 줄바꿈 처리
- **Korean document metadata extraction** / 한국어 문서 메타데이터 추출

## Supported Formats / 지원 형식

- **Documents**: PDF, DOCX, PPTX, XLSX, CSV / 문서: PDF, DOCX, PPTX, XLSX, CSV
- **Web**: HTML, RSS, Wikipedia pages / 웹: HTML, RSS, 위키피디아 페이지
- **Media**: Images (with OCR), Audio (with transcription) / 미디어: 이미지(OCR 포함), 오디오(전사 포함)
- **Data**: JSON, XML, Jupyter Notebooks / 데이터: JSON, XML, Jupyter 노트북
- **Archives**: ZIP, EPUB / 아카이브: ZIP, EPUB
- **Other**: Outlook MSG, YouTube transcripts / 기타: Outlook MSG, YouTube 자막

## Installation / 설치

### Basic Installation / 기본 설치
```bash
pip install voidlight-markitdown
```

### With All Features / 모든 기능 포함
```bash
pip install voidlight-markitdown[all]
```

### With Korean Support / 한국어 지원 포함
```bash
pip install voidlight-markitdown[korean]
```

## Usage / 사용법

### Basic Usage / 기본 사용법

```python
from voidlight_markitdown import VoidLightMarkItDown

# Initialize converter / 변환기 초기화
converter = VoidLightMarkItDown()

# Convert a file / 파일 변환
result = converter.convert("document.pdf")
print(result.markdown)
```

### Korean Mode / 한국어 모드

```python
# Enable Korean mode for better Korean document processing
# 한국어 문서 처리 개선을 위한 한국어 모드 활성화
converter = VoidLightMarkItDown(korean_mode=True)

# Convert Korean document / 한국어 문서 변환
result = converter.convert("korean_document.docx")
print(result.markdown)
```

### Command Line / 명령줄

```bash
# Basic conversion / 기본 변환
voidlight-markitdown input.pdf -o output.md

# With Korean mode / 한국어 모드 사용
voidlight-markitdown --korean-mode korean_doc.pdf -o output.md

# From URI / URI에서 변환
voidlight-markitdown https://example.com/document.pdf
```

## Examples / 예제

### Converting Korean PDF / 한국어 PDF 변환

```python
converter = VoidLightMarkItDown(
    korean_mode=True,
    normalize_korean=True  # Normalize Korean text
)

# Convert Korean PDF with optimal settings
# 최적 설정으로 한국어 PDF 변환
result = converter.convert("korean_research_paper.pdf")

# Access metadata / 메타데이터 접근
if result.metadata:
    print(f"Korean ratio: {result.metadata.get('korean_ratio', 0):.2%}")
    print(f"Has Hanja: {result.metadata.get('has_hanja', False)}")
```

### Processing Mixed Language Documents / 다국어 문서 처리

```python
# Documents with Korean, English, and Chinese
# 한국어, 영어, 중국어가 포함된 문서
converter = VoidLightMarkItDown(korean_mode=True)

result = converter.convert_uri("file:///path/to/mixed_language.docx")
print(result.markdown)
```

## Configuration / 설정

### Environment Variables / 환경 변수

- `VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS` - Enable/disable plugins / 플러그인 활성화/비활성화
- `OPENAI_API_KEY` - For LLM features / LLM 기능용

### Options / 옵션

- `korean_mode` - Enable Korean processing optimizations / 한국어 처리 최적화 활성화
- `normalize_korean` - Normalize Korean text (default: True) / 한국어 텍스트 정규화 (기본값: True)
- `enable_plugins` - Enable plugin support / 플러그인 지원 활성화
- `disable_text_extraction` - Disable text extraction from binary formats / 바이너리 형식에서 텍스트 추출 비활성화

## Plugin Development / 플러그인 개발

```python
# Create a custom converter plugin / 사용자 정의 변환기 플러그인 생성
from voidlight_markitdown._base_converter import DocumentConverter

class MyConverter(DocumentConverter):
    def convert(self, file_path, **kwargs):
        # Your conversion logic / 변환 로직
        pass
```

## License / 라이선스

This project is licensed under the MIT License. See the LICENSE file for details.

이 프로젝트는 MIT 라이선스에 따라 라이선스가 부여됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.

## Acknowledgments / 감사의 말

This project is based on the original MarkItDown project, with enhancements for Korean language support.

이 프로젝트는 원본 MarkItDown 프로젝트를 기반으로 하며, 한국어 지원이 강화되었습니다.