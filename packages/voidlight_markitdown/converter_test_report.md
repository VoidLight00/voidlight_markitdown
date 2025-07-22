
# VoidLight MarkItDown Test Report

## Summary
- Total tests: 35
- ✅ Successful: 23
- ❌ Failed: 11
- ⚠️  Skipped: 1
- Success rate: 65.7%

## Converter Status

### PlainTextConverter
Status: ✅ **WORKING**

- ✅ test.json

### HtmlConverter
Status: ✅ **WORKING**

- ✅ test_blog.html
- ✅ test_blog.html
- ✅ test_wikipedia.html
- ✅ test_wikipedia.html
- ✅ test_serp.html
- ✅ test_serp.html

### RssConverter
Status: ✅ **WORKING**

- ✅ test_rss.xml

### WikipediaConverter
Status: ✅ **WORKING**

- ✅ test_wikipedia.html
- ✅ test_wikipedia.html

### YouTubeConverter
Status: ⚠️  **SKIPPED**

- ⚠️  N/A: No test files available for this converter

### BingSerpConverter
Status: ✅ **WORKING**

- ✅ test_serp.html
- ✅ test_serp.html

### DocxConverter
Status: ❌ **FAILING**

- ❌ test.docx: FileConversionException: File conversion failed after 1 attempts:
- ❌ test.docx: FileConversionException: File conversion failed after 1 attempts:
- ❌ equations.docx: FileConversionException: File conversion failed after 1 attempts:
- ❌ equations.docx: FileConversionException: File conversion failed after 1 attempts:
- ❌ test_with_comment.docx: FileConversionException: File conversion failed after 1 attempts:
- ❌ test_with_comment.docx: FileConversionException: File conversion failed after 1 attempts:

### XlsxConverter
Status: ❌ **FAILING**

- ❌ test.xlsx: FileConversionException: File conversion failed after 1 attempts:

### XlsConverter
Status: ❌ **FAILING**

- ❌ test.xls: FileConversionException: File conversion failed after 1 attempts:

### PptxConverter
Status: ❌ **FAILING**

- ❌ test.pptx: FileConversionException: File conversion failed after 1 attempts:

### AudioConverter
Status: ✅ **WORKING**

- ✅ test.mp3
- ✅ test.m4a
- ✅ test.wav

### ImageConverter
Status: ✅ **WORKING**

- ✅ test.jpg
- ✅ test_llm.jpg

### IpynbConverter
Status: ✅ **WORKING**

- ✅ test_notebook.ipynb

### PdfConverter
Status: ✅ **WORKING**

- ✅ test.pdf
- ✅ test.pdf

### OutlookMsgConverter
Status: ❌ **FAILING**

- ❌ test_outlook_msg.msg: FileConversionException: File conversion failed after 2 attempts:

### EpubConverter
Status: ❌ **FAILING**

- ❌ test.epub: FileConversionException: File conversion failed after 1 attempts:

### ZipConverter
Status: ✅ **WORKING**

- ✅ test_files.zip

### CsvConverter
Status: ✅ **WORKING**

- ✅ test_mskanji.csv
- ✅ test_mskanji.csv

## Detailed Failure Information

### DocxConverter - test.docx
```
FileConversionException: File conversion failed after 1 attempts:
 - DocxConverter threw MissingDependencyException with message: DocxConverter recognized the input as a potential .docx file, but the dependencies needed to read .docx files have not been installed. To resolve this error, include the optional dependency [docx] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[docx]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[docx, ...]
* etc.

Traceback (most recent call last):
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/test_all_converters.py", line 90, in test_converter
    result = md.convert(str(file_path))
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 284, in convert
    return self.convert_local(source, stream_info=stream_info, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 338, in convert_local
    return self._convert(file_stream=fh, stream_info_guesses=guesses, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 636, in _convert
    raise FileConversionException(attempts=failed_attempts)
voidlight_markitdown._exceptions.FileConversionException: File conversion failed after 1 attempts:
 - DocxConverter threw MissingDependencyException with message: DocxConverter recognized the input as a potential .docx file, but the dependencies needed to read .docx files have not been installed. To resolve this error, include the optional dependency [docx] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[docx]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[docx, ...]
* etc.

```

### DocxConverter - test.docx
```
FileConversionException: File conversion failed after 1 attempts:
 - DocxConverter threw MissingDependencyException with message: DocxConverter recognized the input as a potential .docx file, but the dependencies needed to read .docx files have not been installed. To resolve this error, include the optional dependency [docx] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[docx]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[docx, ...]
* etc.

Traceback (most recent call last):
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/test_all_converters.py", line 90, in test_converter
    result = md.convert(str(file_path))
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 284, in convert
    return self.convert_local(source, stream_info=stream_info, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 338, in convert_local
    return self._convert(file_stream=fh, stream_info_guesses=guesses, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 636, in _convert
    raise FileConversionException(attempts=failed_attempts)
voidlight_markitdown._exceptions.FileConversionException: File conversion failed after 1 attempts:
 - DocxConverter threw MissingDependencyException with message: DocxConverter recognized the input as a potential .docx file, but the dependencies needed to read .docx files have not been installed. To resolve this error, include the optional dependency [docx] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[docx]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[docx, ...]
* etc.

```

### DocxConverter - equations.docx
```
FileConversionException: File conversion failed after 1 attempts:
 - DocxConverter threw MissingDependencyException with message: DocxConverter recognized the input as a potential .docx file, but the dependencies needed to read .docx files have not been installed. To resolve this error, include the optional dependency [docx] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[docx]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[docx, ...]
* etc.

Traceback (most recent call last):
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/test_all_converters.py", line 90, in test_converter
    result = md.convert(str(file_path))
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 284, in convert
    return self.convert_local(source, stream_info=stream_info, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 338, in convert_local
    return self._convert(file_stream=fh, stream_info_guesses=guesses, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 636, in _convert
    raise FileConversionException(attempts=failed_attempts)
voidlight_markitdown._exceptions.FileConversionException: File conversion failed after 1 attempts:
 - DocxConverter threw MissingDependencyException with message: DocxConverter recognized the input as a potential .docx file, but the dependencies needed to read .docx files have not been installed. To resolve this error, include the optional dependency [docx] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[docx]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[docx, ...]
* etc.

```

### DocxConverter - equations.docx
```
FileConversionException: File conversion failed after 1 attempts:
 - DocxConverter threw MissingDependencyException with message: DocxConverter recognized the input as a potential .docx file, but the dependencies needed to read .docx files have not been installed. To resolve this error, include the optional dependency [docx] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[docx]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[docx, ...]
* etc.

Traceback (most recent call last):
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/test_all_converters.py", line 90, in test_converter
    result = md.convert(str(file_path))
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 284, in convert
    return self.convert_local(source, stream_info=stream_info, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 338, in convert_local
    return self._convert(file_stream=fh, stream_info_guesses=guesses, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 636, in _convert
    raise FileConversionException(attempts=failed_attempts)
voidlight_markitdown._exceptions.FileConversionException: File conversion failed after 1 attempts:
 - DocxConverter threw MissingDependencyException with message: DocxConverter recognized the input as a potential .docx file, but the dependencies needed to read .docx files have not been installed. To resolve this error, include the optional dependency [docx] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[docx]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[docx, ...]
* etc.

```

### DocxConverter - test_with_comment.docx
```
FileConversionException: File conversion failed after 1 attempts:
 - DocxConverter threw MissingDependencyException with message: DocxConverter recognized the input as a potential .docx file, but the dependencies needed to read .docx files have not been installed. To resolve this error, include the optional dependency [docx] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[docx]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[docx, ...]
* etc.

Traceback (most recent call last):
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/test_all_converters.py", line 90, in test_converter
    result = md.convert(str(file_path))
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 284, in convert
    return self.convert_local(source, stream_info=stream_info, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 338, in convert_local
    return self._convert(file_stream=fh, stream_info_guesses=guesses, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 636, in _convert
    raise FileConversionException(attempts=failed_attempts)
voidlight_markitdown._exceptions.FileConversionException: File conversion failed after 1 attempts:
 - DocxConverter threw MissingDependencyException with message: DocxConverter recognized the input as a potential .docx file, but the dependencies needed to read .docx files have not been installed. To resolve this error, include the optional dependency [docx] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[docx]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[docx, ...]
* etc.

```

### DocxConverter - test_with_comment.docx
```
FileConversionException: File conversion failed after 1 attempts:
 - DocxConverter threw MissingDependencyException with message: DocxConverter recognized the input as a potential .docx file, but the dependencies needed to read .docx files have not been installed. To resolve this error, include the optional dependency [docx] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[docx]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[docx, ...]
* etc.

Traceback (most recent call last):
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/test_all_converters.py", line 90, in test_converter
    result = md.convert(str(file_path))
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 284, in convert
    return self.convert_local(source, stream_info=stream_info, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 338, in convert_local
    return self._convert(file_stream=fh, stream_info_guesses=guesses, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 636, in _convert
    raise FileConversionException(attempts=failed_attempts)
voidlight_markitdown._exceptions.FileConversionException: File conversion failed after 1 attempts:
 - DocxConverter threw MissingDependencyException with message: DocxConverter recognized the input as a potential .docx file, but the dependencies needed to read .docx files have not been installed. To resolve this error, include the optional dependency [docx] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[docx]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[docx, ...]
* etc.

```

### XlsxConverter - test.xlsx
```
FileConversionException: File conversion failed after 1 attempts:
 - XlsxConverter threw MissingDependencyException with message: XlsxConverter recognized the input as a potential .xlsx file, but the dependencies needed to read .xlsx files have not been installed. To resolve this error, include the optional dependency [xlsx] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[xlsx]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[xlsx, ...]
* etc.

Traceback (most recent call last):
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/test_all_converters.py", line 90, in test_converter
    result = md.convert(str(file_path))
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 284, in convert
    return self.convert_local(source, stream_info=stream_info, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 338, in convert_local
    return self._convert(file_stream=fh, stream_info_guesses=guesses, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 636, in _convert
    raise FileConversionException(attempts=failed_attempts)
voidlight_markitdown._exceptions.FileConversionException: File conversion failed after 1 attempts:
 - XlsxConverter threw MissingDependencyException with message: XlsxConverter recognized the input as a potential .xlsx file, but the dependencies needed to read .xlsx files have not been installed. To resolve this error, include the optional dependency [xlsx] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[xlsx]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[xlsx, ...]
* etc.

```

### XlsConverter - test.xls
```
FileConversionException: File conversion failed after 1 attempts:
 - XlsConverter threw MissingDependencyException with message: XlsConverter recognized the input as a potential .xls file, but the dependencies needed to read .xls files have not been installed. To resolve this error, include the optional dependency [xls] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[xls]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[xls, ...]
* etc.

Traceback (most recent call last):
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/test_all_converters.py", line 90, in test_converter
    result = md.convert(str(file_path))
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 284, in convert
    return self.convert_local(source, stream_info=stream_info, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 338, in convert_local
    return self._convert(file_stream=fh, stream_info_guesses=guesses, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 636, in _convert
    raise FileConversionException(attempts=failed_attempts)
voidlight_markitdown._exceptions.FileConversionException: File conversion failed after 1 attempts:
 - XlsConverter threw MissingDependencyException with message: XlsConverter recognized the input as a potential .xls file, but the dependencies needed to read .xls files have not been installed. To resolve this error, include the optional dependency [xls] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[xls]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[xls, ...]
* etc.

```

### PptxConverter - test.pptx
```
FileConversionException: File conversion failed after 1 attempts:
 - PptxConverter threw MissingDependencyException with message: PptxConverter recognized the input as a potential .pptx file, but the dependencies needed to read .pptx files have not been installed. To resolve this error, include the optional dependency [pptx] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[pptx]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[pptx, ...]
* etc.

Traceback (most recent call last):
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/test_all_converters.py", line 90, in test_converter
    result = md.convert(str(file_path))
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 284, in convert
    return self.convert_local(source, stream_info=stream_info, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 338, in convert_local
    return self._convert(file_stream=fh, stream_info_guesses=guesses, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 636, in _convert
    raise FileConversionException(attempts=failed_attempts)
voidlight_markitdown._exceptions.FileConversionException: File conversion failed after 1 attempts:
 - PptxConverter threw MissingDependencyException with message: PptxConverter recognized the input as a potential .pptx file, but the dependencies needed to read .pptx files have not been installed. To resolve this error, include the optional dependency [pptx] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[pptx]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[pptx, ...]
* etc.

```

### OutlookMsgConverter - test_outlook_msg.msg
```
FileConversionException: File conversion failed after 2 attempts:
 - OutlookMsgConverter threw MissingDependencyException with message: OutlookMsgConverter recognized the input as a potential .msg file, but the dependencies needed to read .msg files have not been installed. To resolve this error, include the optional dependency [outlook] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[outlook]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[outlook, ...]
* etc.
 - OutlookMsgConverter threw MissingDependencyException with message: OutlookMsgConverter recognized the input as a potential .msg file, but the dependencies needed to read .msg files have not been installed. To resolve this error, include the optional dependency [outlook] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[outlook]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[outlook, ...]
* etc.

Traceback (most recent call last):
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/test_all_converters.py", line 90, in test_converter
    result = md.convert(str(file_path))
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 284, in convert
    return self.convert_local(source, stream_info=stream_info, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 338, in convert_local
    return self._convert(file_stream=fh, stream_info_guesses=guesses, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 636, in _convert
    raise FileConversionException(attempts=failed_attempts)
voidlight_markitdown._exceptions.FileConversionException: File conversion failed after 2 attempts:
 - OutlookMsgConverter threw MissingDependencyException with message: OutlookMsgConverter recognized the input as a potential .msg file, but the dependencies needed to read .msg files have not been installed. To resolve this error, include the optional dependency [outlook] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[outlook]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[outlook, ...]
* etc.
 - OutlookMsgConverter threw MissingDependencyException with message: OutlookMsgConverter recognized the input as a potential .msg file, but the dependencies needed to read .msg files have not been installed. To resolve this error, include the optional dependency [outlook] or [all] when installing VoidLight MarkItDown. For example:

* pip install voidlight-markitdown[outlook]
* pip install voidlight-markitdown[all]
* pip install voidlight-markitdown[outlook, ...]
* etc.

```

### EpubConverter - test.epub
```
FileConversionException: File conversion failed after 1 attempts:
 - EpubConverter threw TypeError with message: __init__() got an unexpected keyword argument 'title'

Traceback (most recent call last):
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/test_all_converters.py", line 90, in test_converter
    result = md.convert(str(file_path))
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 284, in convert
    return self.convert_local(source, stream_info=stream_info, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 338, in convert_local
    return self._convert(file_stream=fh, stream_info_guesses=guesses, **kwargs)
  File "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/src/voidlight_markitdown/_voidlight_markitdown.py", line 636, in _convert
    raise FileConversionException(attempts=failed_attempts)
voidlight_markitdown._exceptions.FileConversionException: File conversion failed after 1 attempts:
 - EpubConverter threw TypeError with message: __init__() got an unexpected keyword argument 'title'

```

