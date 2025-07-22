#!/usr/bin/env python
"""
Command-line interface for configuring VoidLight MarkItDown logging.

This module provides utilities to:
- Set logging levels
- Configure log output destinations
- Enable/disable structured logging
- View current logging configuration
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

from ._logging import setup_logging, get_log_level


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Configure VoidLight MarkItDown logging",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Set log level to DEBUG
  python -m voidlight_markitdown.cli_logging --level DEBUG
  
  # Enable file logging
  python -m voidlight_markitdown.cli_logging --file voidlight.log
  
  # Use structured JSON logging
  python -m voidlight_markitdown.cli_logging --structured
  
  # Use configuration file
  python -m voidlight_markitdown.cli_logging --config logging.yaml
  
  # Set environment variables for persistent configuration
  export VOIDLIGHT_LOG_LEVEL=DEBUG
  export VOIDLIGHT_LOG_FILE=/var/log/voidlight.log
"""
    )
    
    parser.add_argument(
        "--level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level"
    )
    
    parser.add_argument(
        "--file",
        type=Path,
        help="Log file path"
    )
    
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to logging configuration file (JSON or YAML)"
    )
    
    parser.add_argument(
        "--structured",
        action="store_true",
        help="Use structured JSON logging"
    )
    
    parser.add_argument(
        "--no-console",
        action="store_true",
        help="Disable console logging"
    )
    
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Use detailed format with file/line info"
    )
    
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=10 * 1024 * 1024,
        help="Maximum log file size before rotation (default: 10MB)"
    )
    
    parser.add_argument(
        "--backup-count",
        type=int,
        default=5,
        help="Number of backup files to keep (default: 5)"
    )
    
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show current logging configuration"
    )
    
    parser.add_argument(
        "--export-env",
        action="store_true",
        help="Export configuration as environment variables"
    )
    
    return parser.parse_args()


def show_config(args):
    """Display current logging configuration."""
    config = {
        "level": os.getenv("VOIDLIGHT_LOG_LEVEL", "INFO"),
        "file": os.getenv("VOIDLIGHT_LOG_FILE", "None"),
        "structured": os.getenv("VOIDLIGHT_LOG_STRUCTURED", "false") == "true",
        "console": os.getenv("VOIDLIGHT_LOG_CONSOLE", "true") == "true",
        "detailed": os.getenv("VOIDLIGHT_LOG_DETAILED", "false") == "true",
        "config_file": os.getenv("VOIDLIGHT_LOG_CONFIG", "None"),
    }
    
    print("Current VoidLight MarkItDown Logging Configuration:")
    print("=" * 50)
    for key, value in config.items():
        print(f"{key:15}: {value}")
    print("=" * 50)
    
    # Show example usage
    print("\nTo make these settings persistent, export environment variables:")
    print(f"export VOIDLIGHT_LOG_LEVEL={config['level']}")
    if config['file'] != "None":
        print(f"export VOIDLIGHT_LOG_FILE={config['file']}")
    if config['structured']:
        print("export VOIDLIGHT_LOG_STRUCTURED=true")
    if not config['console']:
        print("export VOIDLIGHT_LOG_CONSOLE=false")
    if config['detailed']:
        print("export VOIDLIGHT_LOG_DETAILED=true")


def export_env(args):
    """Export configuration as environment variables."""
    exports = []
    
    if args.level:
        exports.append(f"export VOIDLIGHT_LOG_LEVEL={args.level}")
    
    if args.file:
        exports.append(f"export VOIDLIGHT_LOG_FILE={args.file}")
    
    if args.structured:
        exports.append("export VOIDLIGHT_LOG_STRUCTURED=true")
    
    if args.no_console:
        exports.append("export VOIDLIGHT_LOG_CONSOLE=false")
    
    if args.detailed:
        exports.append("export VOIDLIGHT_LOG_DETAILED=true")
    
    if args.config:
        exports.append(f"export VOIDLIGHT_LOG_CONFIG={args.config}")
    
    if exports:
        print("# Add these lines to your shell configuration:")
        for export in exports:
            print(export)
    else:
        print("# No configuration changes specified")


def main():
    """Main entry point."""
    args = parse_args()
    
    if args.show_config:
        show_config(args)
        return
    
    if args.export_env:
        export_env(args)
        return
    
    # Apply configuration
    setup_logging(
        level=args.level,
        log_file=args.file,
        structured=args.structured,
        console=not args.no_console,
        detailed=args.detailed,
        max_bytes=args.max_bytes,
        backup_count=args.backup_count,
        config_file=args.config,
    )
    
    # Test logging
    from . import VoidLightMarkItDown
    converter = VoidLightMarkItDown()
    
    print("Logging configuration applied successfully!")
    print(f"Log level: {args.level or os.getenv('VOIDLIGHT_LOG_LEVEL', 'INFO')}")
    if args.file:
        print(f"Log file: {args.file}")
    if args.structured:
        print("Using structured JSON logging")
    if args.config:
        print(f"Using configuration file: {args.config}")


if __name__ == "__main__":
    main()