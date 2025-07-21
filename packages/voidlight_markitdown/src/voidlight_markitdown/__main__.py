#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from typing import Optional
from ._voidlight_markitdown import VoidLightMarkItDown
from ._exceptions import FileConversionException


def main():
    parser = argparse.ArgumentParser(
        description="VoidLight MarkItDown - Convert documents to Markdown with enhanced Korean support."
    )
    
    parser.add_argument(
        "input",
        nargs="?",
        help="Input file path or URI (http://, https://, file://, or data://). If not provided, reads from stdin."
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path. If not provided, writes to stdout."
    )
    
    parser.add_argument(
        "--korean-mode",
        action="store_true",
        help="Enable Korean text processing mode for better Korean document handling."
    )
    
    parser.add_argument(
        "--no-normalize-korean",
        action="store_true",
        help="Disable Korean text normalization when in Korean mode."
    )
    
    parser.add_argument(
        "--enable-plugins",
        action="store_true",
        help="Enable plugin support."
    )
    
    parser.add_argument(
        "--disable-text-extraction",
        action="store_true",
        help="Disable text extraction from binary formats."
    )
    
    args = parser.parse_args()
    
    # Initialize VoidLightMarkItDown
    converter = VoidLightMarkItDown(
        enable_plugins=args.enable_plugins,
        korean_mode=args.korean_mode,
        normalize_korean=not args.no_normalize_korean,
        disable_text_extraction=args.disable_text_extraction
    )
    
    try:
        # Handle input
        if args.input:
            # Convert from file or URI
            result = converter.convert_uri(args.input)
        else:
            # Read from stdin
            import io
            stdin_bytes = sys.stdin.buffer.read()
            result = converter.convert_stream(io.BytesIO(stdin_bytes))
        
        # Handle output
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(result.markdown, encoding='utf-8')
            print(f"Converted successfully. Output written to: {args.output}")
        else:
            # Write to stdout
            print(result.markdown)
            
    except FileConversionException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()