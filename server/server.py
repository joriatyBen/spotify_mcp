from typing import Any, Dict, List
import httpx
from mcp.server.fastmcp import FastMCP
import os
import base64
import requests
import asyncpraw


mcp = FastMCP("spotify")

SPOTIFY_API_BASE = "https://api.spotify.com/v1"


async def _authorize_to_spotify() -> str:
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    if not client_id or not client_secret:
        raise ValueError("CLIENT_ID and CLIENT_SECRET must be set in environment variables")

    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        'Authorization': f'Basic {encoded_credentials}'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    
    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise RuntimeError(f"Failed to get token: {response.status_code} {response.text}")


async def _request_spotify(url: str, token: str) -> Dict[str, Any] | None:
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"request error: {e}")
            return None

async def _map_artist_title(data: Dict[str, Any]) -> List[str]:
    artist_track_list = []

    for item in data.get("items", []):
        track = item.get("track", {})
        track_name = track.get("name")
        artists = track.get("artists", [])
        for artist in artists:
            artist_name = artist.get("name")
            artist_track_list.append(f"artist: {artist_name}, track: {track_name}")

    return artist_track_list

@mcp.tool(
    name="get_playlist_titles_and_artists",
    description="Retrieves all tracks from a specific Spotify playlist, returning a list of artist and track name pairs. Requires SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, and PLAYLIST_ID environment variables."
)
async def get_playlist_titles_and_artists() -> List[str]:
    url = f"{SPOTIFY_API_BASE}/playlists/{os.getenv('PLAYLIST_ID')}/tracks?limit=100"
    print(url)

    auth_token = await _authorize_to_spotify()
    data = await _request_spotify(url, auth_token)
    
    if not data:
        print("Server found no valid playlist data")
        return []
    
    return await _map_artist_title(data)

@mcp.tool(
    name="crawl_subreddit_recommendations",
    description="Crawls the r/punk subreddit to find band recommendations from recent posts and comments. Searches for recommendation keywords like 'recommend', 'check out', 'similar to', etc. Requires REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and REDDIT_USERNAME environment variables."
)
async def crawl_subreddit_recomments() -> str:
    # Authenticate using environment variables
    reddit = asyncpraw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=f"spotimcp/0.1 by {os.getenv('REDDIT_USERNAME')}"
    )
    
    try:
        # Choose the punk subreddit
        subreddit = await reddit.subreddit("punk")
        
        # Keywords that might indicate band recommendations
        recommendation_keywords = [
            "recommend", "check out", "similar to", "sounds like",
            "band", "listen to", "you might like", "reminds me of"
        ]
        
        recommendations = []
        
        # Get top 25 hot posts
        async for post in subreddit.hot(limit=25):
            # Check if post title might contain band recommendations
            post_text = post.title.lower() + " " + post.selftext.lower()
            
            # Check if post might be about band recommendations
            if any(keyword in post_text for keyword in recommendation_keywords):
                recommendations.append(f"From post '{post.title}':")
                
                # Extract potential band names from post text
                for line in post.selftext.split('\n'):
                    if any(keyword in line.lower() for keyword in recommendation_keywords):
                        recommendations.append(f"  • {line.strip()}")
            
            # Check comments for recommendations (limit to top 10 comments)
            try:
                await post.comments.replace_more(limit=0)  # Remove MoreComments objects
                comment_count = 0
                async for comment in post.comments:
                    if comment_count >= 10:
                        break
                    
                    comment_text = comment.body.lower()
                    
                    # Check if comment might contain band recommendations
                    if any(keyword in comment_text for keyword in recommendation_keywords):
                        recommendations.append(f"From comment on '{post.title}':")
                        recommendations.append(f"  • {comment.body.strip()}")
                    
                    comment_count += 1
            except Exception as e:
                print(f"Error processing comments: {e}")
        
        # Format results as a string
        if recommendations:
            result = "Band recommendations from r/punk:\n" + "\n".join(recommendations)
        else:
            result = "No band recommendations found in r/punk subreddit."
        
        return result
    finally:
        # Ensure the Reddit client is closed
        await reddit.close()

if __name__ == "__main__":
    mcp.run(transport='stdio')
