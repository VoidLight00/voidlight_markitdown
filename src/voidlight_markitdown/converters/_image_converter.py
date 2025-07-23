from typing import BinaryIO, Any, Union, Optional
import base64
import mimetypes
from ._exiftool import exiftool_metadata
from .base import DocumentConverter, DocumentConverterResult
from ..core.stream_info import StreamInfo

# Optional OCR imports
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    import io
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

ACCEPTED_MIME_TYPE_PREFIXES = [
    "image/jpeg",
    "image/png",
]

ACCEPTED_FILE_EXTENSIONS = [".jpg", ".jpeg", ".png"]


class ImageConverter(DocumentConverter):
    """
    Converts images to markdown via extraction of metadata (if `exiftool` is installed), and description via a multimodal LLM (if an llm_client is configured).
    Enhanced with Korean OCR support using EasyOCR.
    """
    
    def __init__(self):
        self.easyocr_reader = None

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> bool:
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()

        if extension in ACCEPTED_FILE_EXTENSIONS:
            return True

        for prefix in ACCEPTED_MIME_TYPE_PREFIXES:
            if mimetype.startswith(prefix):
                return True

        return False

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        md_content = ""
        korean_mode = kwargs.get('korean_mode', False)

        # Add metadata
        metadata = exiftool_metadata(
            file_stream, exiftool_path=kwargs.get("exiftool_path")
        )

        if metadata:
            for f in [
                "ImageSize",
                "Title",
                "Caption",
                "Description",
                "Keywords",
                "Artist",
                "Author",
                "DateTimeOriginal",
                "CreateDate",
                "GPSPosition",
            ]:
                if f in metadata:
                    md_content += f"{f}: {metadata[f]}\n"

        # Try OCR if requested or in Korean mode
        perform_ocr = kwargs.get('perform_ocr', korean_mode)
        if perform_ocr:
            ocr_text = self._perform_ocr(file_stream, korean_mode=korean_mode)
            if ocr_text:
                md_content += "\n# OCR Text:\n" + ocr_text.strip() + "\n"
        
        # Try describing the image with GPT
        llm_client = kwargs.get("llm_client")
        llm_model = kwargs.get("llm_model")
        if llm_client is not None and llm_model is not None:
            llm_description = self._get_llm_description(
                file_stream,
                stream_info,
                client=llm_client,
                model=llm_model,
                prompt=kwargs.get("llm_prompt"),
            )

            if llm_description is not None:
                md_content += "\n# Description:\n" + llm_description.strip() + "\n"

        return DocumentConverterResult(
            markdown=md_content,
        )

    def _get_llm_description(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        *,
        client,
        model,
        prompt=None,
    ) -> Optional[str]:
        if prompt is None or prompt.strip() == "":
            # Check for Korean mode
            korean_mode = kwargs.get('korean_mode', False)
            if korean_mode:
                prompt = "이 이미지에 대한 자세한 설명을 한국어로 작성해주세요. 이미지에 텍스트가 있다면 그 내용도 포함해주세요."
            else:
                prompt = "Write a detailed caption for this image."

        # Get the content type
        content_type = stream_info.mimetype
        if not content_type:
            content_type, _ = mimetypes.guess_type(
                "_dummy" + (stream_info.extension or "")
            )
        if not content_type:
            content_type = "application/octet-stream"

        # Convert to base64
        cur_pos = file_stream.tell()
        try:
            base64_image = base64.b64encode(file_stream.read()).decode("utf-8")
        except Exception as e:
            return None
        finally:
            file_stream.seek(cur_pos)

        # Prepare the data-uri
        data_uri = f"data:{content_type};base64,{base64_image}"

        # Prepare the OpenAI API request
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_uri,
                        },
                    },
                ],
            }
        ]

        # Call the OpenAI API
        response = client.chat.completions.create(model=model, messages=messages)
        return response.choices[0].message.content
    
    def _perform_ocr(self, file_stream: BinaryIO, korean_mode: bool = False) -> str:
        """Perform OCR on the image."""
        cur_pos = file_stream.tell()
        try:
            # Try EasyOCR first for Korean
            if korean_mode and EASYOCR_AVAILABLE:
                if self.easyocr_reader is None:
                    # Initialize reader with Korean and English
                    self.easyocr_reader = easyocr.Reader(['ko', 'en'], gpu=False)
                
                # Read image data
                file_stream.seek(0)
                image_data = file_stream.read()
                
                # Perform OCR
                result = self.easyocr_reader.readtext(image_data, detail=0)
                return '\n'.join(result) if result else ""
            
            # Fallback to pytesseract
            elif PYTESSERACT_AVAILABLE:
                file_stream.seek(0)
                image = Image.open(file_stream)
                
                # Set language for pytesseract
                lang = 'kor+eng' if korean_mode else 'eng'
                try:
                    return pytesseract.image_to_string(image, lang=lang)
                except:
                    # Fallback to English only if Korean fails
                    return pytesseract.image_to_string(image, lang='eng')
            
            return ""
            
        except Exception as e:
            return ""
        finally:
            file_stream.seek(cur_pos)
