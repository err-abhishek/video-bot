import asyncio
from yt_dlp import YoutubeDL
import os

async def download_video(video, save_dir):
    """Download video using yt-dlp and return title, file path, and URL."""
    title = video.get('title', 'unknown').replace(" ", "_").replace("/", "-")
    save_path = os.path.join(save_dir, f"{title}.mp4")
    url = video.get('webpage_url')

    ydl_opts = {
        'outtmpl': save_path,
        'quiet': False,
        'format': 'mp4'
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"Downloading: {title}")
            ydl.download([url])
            print(f"Downloaded: {save_path}")
            return title, save_path, url  # Include URL in the return value
        except Exception as e:
            print(f"Failed to download video {title}: {e}")
            return None, None, None  # Ensure the structure matches (title, path, url)

async def search_and_download_videos(keyword, max_results=10, save_dir="./videos"):
    """
    Search YouTube for videos based on a keyword.
    Filter videos that are between 7 and 60 seconds.
    """
    os.makedirs(save_dir, exist_ok=True)
    ydl_opts = {
        'quiet': True,
        'noplaylist': True,
        'max_downloads': max_results,
        'format': 'mp4'
    }
    downloaded_videos = []
    with YoutubeDL(ydl_opts) as ydl:
        try:
            # Search for videos
            results = ydl.extract_info(f"ytsearch{max_results}:{keyword}", download=False)
            videos = results.get('entries', [])
            if not videos:
                print(f"No videos found for keyword: {keyword}")
                return []

            # Filter videos by duration (7 to 60 seconds)
            filtered_videos = [
                video for video in videos if 7 <= video.get('duration', 0) <= 60
            ]

            if not filtered_videos:
                print(f"No videos between 7-60 seconds for keyword: {keyword}")
                return []

            print(f"Found {len(filtered_videos)} videos between 7-60 seconds.")

            # Download each valid video
            tasks = [download_video(video, save_dir) for video in filtered_videos]
            downloaded_videos = await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Error during search or download: {e}")
    return downloaded_videos  # List of (title, path, url) tuples
