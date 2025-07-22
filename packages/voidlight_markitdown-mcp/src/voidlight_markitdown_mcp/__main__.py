import contextlib
import sys
import os
import logging
from collections.abc import AsyncIterator
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send
from mcp.server import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from voidlight_markitdown import VoidLightMarkItDown
from voidlight_markitdown._logging import setup_logging, get_logger
import uvicorn

# Initialize FastMCP server for VoidLight MarkItDown (SSE)
mcp = FastMCP("voidlight_markitdown")

# Setup logging for MCP server
logger = get_logger("voidlight_markitdown.mcp")


@mcp.tool()
async def convert_to_markdown(uri: str) -> str:
    """Convert a resource described by an http:, https:, file: or data: URI to markdown with enhanced Korean support"""
    logger.info(f"MCP: Converting URI to markdown", uri=uri)
    try:
        result = VoidLightMarkItDown(enable_plugins=check_plugins_enabled()).convert_uri(uri).markdown
        logger.info(f"MCP: Conversion successful", uri=uri, result_size=len(result))
        return result
    except Exception as e:
        logger.error(f"MCP: Conversion failed", uri=uri, error=str(e), exc_info=True)
        raise


@mcp.tool()
async def convert_korean_document(uri: str, normalize_korean: bool = True) -> str:
    """Convert Korean documents with advanced text normalization and encoding handling
    
    Args:
        uri: Document URI (http:, https:, file: or data:)
        normalize_korean: Whether to normalize Korean text (default: True)
    """
    logger.info(f"MCP: Converting Korean document", uri=uri, normalize_korean=normalize_korean)
    try:
        converter = VoidLightMarkItDown(
            enable_plugins=check_plugins_enabled(),
            korean_mode=True,
            normalize_korean=normalize_korean
        )
        result = converter.convert_uri(uri).markdown
        logger.info(f"MCP: Korean conversion successful", uri=uri, result_size=len(result))
        return result
    except Exception as e:
        logger.error(f"MCP: Korean conversion failed", uri=uri, error=str(e), exc_info=True)
        raise


def check_plugins_enabled() -> bool:
    return os.getenv("VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS", "false").strip().lower() in (
        "true",
        "1",
        "yes",
    )


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    sse = SseServerTransport("/messages/")
    session_manager = StreamableHTTPSessionManager(
        app=mcp_server,
        event_store=None,
        json_response=True,
        stateless=True,
    )

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            print("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                print("Application shutting down...")

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/mcp", app=handle_streamable_http),
            Mount("/messages/", app=sse.handle_post_message),
        ],
        lifespan=lifespan,
    )


# Main entry point
def main():
    import argparse
    
    # Setup logging based on environment variable
    log_level = os.getenv("VOIDLIGHT_LOG_LEVEL", "INFO")
    log_file = os.getenv("VOIDLIGHT_LOG_FILE")
    
    setup_logging(
        level=log_level,
        log_file=log_file,
        console=True,
        detailed=log_level == "DEBUG"
    )
    
    logger.info("Starting VoidLight MarkItDown MCP server")

    mcp_server = mcp._mcp_server

    parser = argparse.ArgumentParser(description="Run a VoidLight MarkItDown MCP server")

    parser.add_argument(
        "--http",
        action="store_true",
        help="Run the server with Streamable HTTP and SSE transport rather than STDIO (default: False)",
    )
    parser.add_argument(
        "--sse",
        action="store_true",
        help="(Deprecated) An alias for --http (default: False)",
    )
    parser.add_argument(
        "--host", default=None, help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=None, help="Port to listen on (default: 3001)"
    )
    args = parser.parse_args()

    use_http = args.http or args.sse

    if not use_http and (args.host or args.port):
        parser.error(
            "Host and port arguments are only valid when using streamable HTTP or SSE transport (see: --http)."
        )
        sys.exit(1)

    if use_http:
        host = args.host if args.host else "127.0.0.1"
        port = args.port if args.port else 3001
        logger.info(f"Starting HTTP/SSE server on {host}:{port}")
        
        starlette_app = create_starlette_app(mcp_server, debug=True)
        uvicorn.run(
            starlette_app,
            host=host,
            port=port,
        )
    else:
        logger.info("Starting STDIO server")
        mcp.run()


if __name__ == "__main__":
    main()