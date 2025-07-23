#!/usr/bin/env python3
"""Remote debugging server for voidlight_markitdown."""

import argparse
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def setup_remote_debugging(host: str = "0.0.0.0", port: int = 5678, wait: bool = True):
    """Setup remote debugging with debugpy.
    
    Args:
        host: Host to listen on
        port: Port to listen on
        wait: Whether to wait for debugger to attach
    """
    try:
        import debugpy
    except ImportError:
        print("Error: debugpy not installed. Install with: pip install debugpy")
        sys.exit(1)
        
    print(f"Starting debug server on {host}:{port}")
    debugpy.listen((host, port))
    
    if wait:
        print("Waiting for debugger to attach...")
        debugpy.wait_for_client()
        print("Debugger attached!")
    else:
        print("Debug server started. Attach debugger when ready.")


def main():
    parser = argparse.ArgumentParser(
        description="Start remote debugging server for voidlight_markitdown"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to listen on (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5678,
        help="Port to listen on (default: 5678)"
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Don't wait for debugger to attach"
    )
    parser.add_argument(
        "--mcp-server",
        action="store_true",
        help="Start MCP server with debugging"
    )
    parser.add_argument(
        "--cli",
        nargs="*",
        help="Run CLI with debugging"
    )
    
    args = parser.parse_args()
    
    # Setup debugging
    setup_remote_debugging(
        host=args.host,
        port=args.port,
        wait=not args.no_wait
    )
    
    # Run the appropriate component
    if args.mcp_server:
        print("Starting MCP server with debugging...")
        from voidlight_markitdown_mcp.server import main as mcp_main
        mcp_main()
    elif args.cli is not None:
        print("Running CLI with debugging...")
        from voidlight_markitdown.__main__ import main as cli_main
        sys.argv = ["voidlight-markitdown"] + args.cli
        cli_main()
    else:
        print("Debug server running. Start your application separately.")
        # Keep the server running
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down debug server.")


if __name__ == "__main__":
    main()