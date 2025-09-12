import asyncio
import logging
import os
import uvicorn
import argparse
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

from server import (
    get_playlist_titles_and_artists,
    crawl_subreddit_recomments,
)

# Load environment variables from client/.env
env_path = Path(__file__).parent.parent / "client" / ".env"
load_dotenv(env_path)

# Map environment variables for compatibility with server.py
if os.getenv('SPOTIFY_PLAYLIST_ID') and not os.getenv('PLAYLIST_ID'):
    os.environ['PLAYLIST_ID'] = os.getenv('SPOTIFY_PLAYLIST_ID')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP instance
mcp = FastMCP("spotify-remote")

@mcp.tool()
async def get_playlist_tracks() -> list[str]:
    """Get track titles and artists from a Spotify playlist"""
    result = await get_playlist_titles_and_artists()
    return result

@mcp.tool()
async def get_band_recommendations() -> str:
    """Crawl the punk subreddit for band recommendations"""
    result = await crawl_subreddit_recomments()
    return result

async def run_streamable_http_server(host: str = "0.0.0.0", port: int = 8080) -> None:
    # Get the underlying server from FastMCP
    server = mcp._mcp_server
    
    # Create the session manager for handling HTTP requests
    # Configure for stateless operation to make testing easier
    session_manager = StreamableHTTPSessionManager(
        app=server,
        event_store=None,  # Could add persistence here if needed
        stateless=True,  # Allow requests without session IDs
        json_response=True  # Return JSON responses instead of SSE
    )
    
    logger.info(f"Starting Streamable HTTP Spotify MCP server on {host}:{port}")
    
    # Create ASGI application handler
    async def asgi_handler(scope, receive, send):
        await session_manager.handle_request(scope, receive, send)
    
    # Run with uvicorn
    try:
        config = uvicorn.Config(
            asgi_handler,
            host=host,
            port=port,
            log_level="info"
        )
        uvicorn_server = uvicorn.Server(config)
        
        # Run the session manager and uvicorn together
        async with session_manager.run():
            await uvicorn_server.serve()
            
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        raise

async def main():
    parser = argparse.ArgumentParser(description="Streamable HTTP Spotify MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    
    args = parser.parse_args()
    
    # Validate environment variables  
    required_vars = ["SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "SPOTIFY_PLAYLIST_ID", "REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return
    
    try:
        await run_streamable_http_server(host=args.host, port=args.port)
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())