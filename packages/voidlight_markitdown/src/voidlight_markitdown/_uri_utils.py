import base64
import mimetypes
from typing import Tuple, Optional
from urllib.parse import urlparse, unquote
from pathlib import Path
import platform


def parse_data_uri(uri: str) -> Tuple[Optional[str], bytes]:
    """Parse a data URI and return mime type and decoded data.
    
    Args:
        uri: Data URI to parse
        
    Returns:
        Tuple of (mime_type, data)
    """
    if not uri.startswith('data:'):
        raise ValueError("Not a data URI")
    
    # Remove the data: prefix
    uri_content = uri[5:]
    
    # Split at the comma
    if ',' not in uri_content:
        raise ValueError("Invalid data URI format")
    
    header, data_part = uri_content.split(',', 1)
    
    # Parse the header
    mime_type = None
    is_base64 = False
    
    if header:
        parts = header.split(';')
        if parts[0] and '/' in parts[0]:
            mime_type = parts[0]
        
        for part in parts[1:]:
            if part.strip() == 'base64':
                is_base64 = True
    
    # Decode the data
    if is_base64:
        data = base64.b64decode(data_part)
    else:
        data = unquote(data_part).encode('utf-8')
    
    return mime_type, data


def file_uri_to_path(uri: str) -> Path:
    """Convert a file:// URI to a Path object.
    
    Args:
        uri: File URI to convert
        
    Returns:
        Path object
    """
    if not uri.startswith('file://'):
        raise ValueError("Not a file URI")
    
    parsed = urlparse(uri)
    
    # Handle Windows paths
    if platform.system() == 'Windows':
        # Windows file URIs can be file:///C:/path or file://server/share
        path = unquote(parsed.path)
        if path.startswith('/') and len(path) > 2 and path[2] == ':':
            # Remove leading slash for absolute Windows paths
            path = path[1:]
    else:
        # Unix paths
        path = unquote(parsed.path)
    
    return Path(path)