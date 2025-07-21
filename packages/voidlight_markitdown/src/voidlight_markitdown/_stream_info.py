from typing import Optional, Union, BinaryIO
from pathlib import Path
import os


class StreamInfo:
    """Information about a stream/file."""
    
    def __init__(
        self,
        stream: BinaryIO,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None,
        encoding: Optional[str] = None
    ):
        self.stream = stream
        self.filename = filename
        self.mime_type = mime_type
        self.encoding = encoding
        
    @property
    def extension(self) -> Optional[str]:
        """Get file extension if filename is available."""
        if self.filename:
            _, ext = os.path.splitext(self.filename)
            return ext.lower()
        return None
    
    def read(self) -> bytes:
        """Read the entire stream content."""
        pos = self.stream.tell()
        self.stream.seek(0)
        content = self.stream.read()
        self.stream.seek(pos)
        return content