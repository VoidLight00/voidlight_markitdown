from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Union, Optional
from pathlib import Path


@dataclass
class DocumentConverterResult:
    """Result of a document conversion."""
    
    markdown: str = ""
    metadata: Optional[Dict[str, Any]] = None


class DocumentConverter(ABC):
    """Base class for all document converters."""
    
    @abstractmethod
    def convert(
        self,
        file_path: Union[str, Path],
        **kwargs: Any
    ) -> DocumentConverterResult:
        """Convert a document to markdown.
        
        Args:
            file_path: Path to the document
            **kwargs: Additional converter-specific options
            
        Returns:
            DocumentConverterResult containing the markdown and metadata
        """
        pass
    
    def can_handle(self, file_path: Union[str, Path]) -> bool:
        """Check if this converter can handle the given file.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if the converter can handle this file type
        """
        return False