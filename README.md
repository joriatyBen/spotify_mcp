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

1. Clone this repository
2. Set up your environment variables in `.env` (see `.env.dist` for required variables)
3. Run the MCP: `uv run client/client.py server/server.py  `
4. Start chatting about music!

## Example Queries

- "Show me tracks from my playlist"
- "Find punk band recommendations from Reddit"
- "What are people recommending in the punk community?"

## 🔒 Privacy

Your Spotify and Reddit credentials are stored locally and only used to access the respective APIs.

---

Made with ❤️ for music lovers