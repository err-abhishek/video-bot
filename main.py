import asyncio
from downloader import search_and_download_videos
from uploader import upload_videos

async def main():
    try:
        keyword = input("Enter a keyword to search Reels (e.g., Motivation): ").strip()

        print(f"Searching and downloading Reels using keyword: {keyword}")
        downloaded_videos = await search_and_download_videos(keyword)

        if not downloaded_videos:
            print("No valid Reels downloaded. Exiting.")
            return

        print("Uploading downloaded Reels...")
        await upload_videos(downloaded_videos)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
