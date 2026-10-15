"""Small YouTube Data API v3 client using Python's standard library."""
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlencode

# Load the project's .env explicitly so this module works whether launched
# from the project root, VS Code, or Uvicorn with a different working directory.
PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env", override=False)
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def search_youtube(topic: str, max_results: int = 8) -> dict:
    """Fetch public YouTube video metadata and public counters, if available."""
    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    if not api_key:
        return {"connected": False, "message": "YOUTUBE_API_KEY is missing from the project .env file.", "videos": []}

    params = urlencode({
        "part": "snippet",
        "q": topic,
        "type": "video",
        "maxResults": max(1, min(int(max_results), 10)),
        "order": "relevance",
        "key": api_key,
    })
    search_url = "https://www.googleapis.com/youtube/v3/search?" + params
    try:
        req = Request(search_url, headers={"Accept": "application/json", "User-Agent": "TubePilot/1.0"})
        with urlopen(req, timeout=15) as response:
            search_data = json.loads(response.read().decode("utf-8"))
        ids = [item.get("id", {}).get("videoId") for item in search_data.get("items", [])]
        ids = [video_id for video_id in ids if video_id]
        if not ids:
            return {"connected": True, "message": "YouTube API connected, but no matching public videos were returned.", "videos": []}

        stats_params = urlencode({"part": "snippet,statistics", "id": ",".join(ids), "key": api_key})
        stats_url = "https://www.googleapis.com/youtube/v3/videos?" + stats_params
        req = Request(stats_url, headers={"Accept": "application/json", "User-Agent": "TubePilot/1.0"})
        with urlopen(req, timeout=15) as response:
            stats_data = json.loads(response.read().decode("utf-8"))

        videos = []
        for item in stats_data.get("items", []):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            videos.append({
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
                "video_id": item.get("id", ""),
                "url": "https://www.youtube.com/watch?v=" + item.get("id", ""),
                "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url") or snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                "views": stats.get("viewCount"),
                "likes": stats.get("likeCount"),
                "comments": stats.get("commentCount"),
            })
        return {"connected": True, "message": f"Fetched {len(videos)} public videos from YouTube Data API v3.", "videos": videos}
    except HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8", errors="replace")[:600]
        except Exception:
            detail = str(exc)
        return {"connected": False, "message": f"YouTube API HTTP {exc.code}: {detail}", "videos": []}
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        return {"connected": False, "message": f"YouTube API request failed: {type(exc).__name__}: {exc}", "videos": []}


def format_youtube_section(data: dict) -> str:
    videos = data.get("videos", [])
    lines = ["## Live YouTube search results (YouTube Data API v3)", "", f"**Connection:** {data.get('message', 'No status available')}", ""]
    if not data.get("connected"):
        lines += ["Live YouTube data was not retrieved for this report. Check the API key, API enablement, and quota.", ""]
    elif not videos:
        lines += ["No matching public video records were returned for this query.", ""]
    else:
        lines += ["| Video | Channel | Published (UTC) | Views | Likes | Comments |", "|---|---|---|---:|---:|---:|"]
        for video in videos:
            title = str(video.get("title", "")).replace("|", "\\|").replace("\n", " ")
            channel = str(video.get("channel", "")).replace("|", "\\|")
            url = video.get("url", "")
            title_cell = f"[{title}]({url})" if url else title
            lines.append("| " + " | ".join([
                title_cell, channel, str(video.get("published_at", "")),
                str(video.get("views") if video.get("views") is not None else "Hidden/unavailable"),
                str(video.get("likes") if video.get("likes") is not None else "Hidden/unavailable"),
                str(video.get("comments") if video.get("comments") is not None else "Hidden/unavailable"),
            ]) + " |")
        lines += ["", "These are public video results and counters, not keyword search-volume estimates or predictions of future views.", ""]
    return "\n".join(lines)
