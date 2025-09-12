# 🎵 Spotify MCP

A handy little tool that combines a Spotify playlist with music recommendations from Reddit.

## What is this?

Spotify MCP is a personal music assistant that helps:

- 🎧 Browse a Spotify playlist
- 🔍 Discover new music recommendations from Reddit communities
- 💬 Chat with Claude AI about music and get personalized suggestions

## How it works

This project uses the Model Control Protocol (MCP) to create a bridge between:

1. **Spotify API** - Access playlist and track information
2. **Reddit API** - Crawl music subreddits for recommendations
3. **Claude AI** - Process your queries and provide intelligent responses

## Quick Start

### Local MCP Server (stdio)
1. Clone this repository
2. Set up your environment variables in `.env` (see `.env.dist` for required variables)
3. Run the MCP: `uv run client/client.py server/server.py`
4. Start chatting about music!

### Remote MCP Server (HTTP)
1. Ensure your environment variables are set in `client/.env` (same as local setup)

2. Start the remote server:
   ```bash
   uv run server/server_remote.py --host 0.0.0.0 --port 8080
   ```

3. Connect from Claude Code by adding to `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "spotify-remote": {
         "command": "mcp-client",
         "args": ["http://localhost:8080"],
         "transport": "streamable-http"
       }
     }
   }
   ```

## Available Tools

- `get_playlist_tracks` - Get track titles and artists from your Spotify playlist
- `get_band_recommendations` - Crawl r/punk subreddit for band recommendations

## Testing the Remote Server

The server is configured for stateless operation for easy testing:

**List available tools:**
```bash
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

**Call a tool:**
```bash
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_playlist_tracks"
    },
    "id": 2
  }'
```

## Example Queries

- "Show me tracks from my playlist"
- "Find punk band recommendations from Reddit"
- "What are people recommending in the punk community?"

## 🔒 Privacy

Your Spotify and Reddit credentials are stored locally and only used to access the respective APIs.

---

Made with ❤️ for music lovers