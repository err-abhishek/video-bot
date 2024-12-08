import aiohttp
import os
import ssl

# Constants
FLIC_TOKEN = "flic_cefe179191b2bc6f84528e3bed920055864cde1d05c27ca553805f2d835f5721"
UPLOAD_URL = "https://api.socialverseapp.com/posts/generate-upload-url"
POST_URL = "https://api.socialverseapp.com/posts"
URL_FILE = "uploaded_video_urls.txt"

# Create an SSL context that does not verify certificates
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def read_uploaded_urls():
    """Read the URLs of already uploaded videos from the file."""
    if not os.path.exists(URL_FILE):
        return set()
    with open(URL_FILE, "r") as file:
        return set(file.read().splitlines())

def write_uploaded_url(url):
    """Write the video URL to the file to keep track of uploaded videos."""
    with open(URL_FILE, "a") as file:
        file.write(url + "\n")

async def get_upload_url():
    """Fetch the pre-signed upload URL."""
    headers = {"Flic-Token": FLIC_TOKEN, "Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(UPLOAD_URL, headers=headers, ssl=ssl_context) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Failed to fetch upload URL: {response.status}")
                return None

async def upload_video(file_path, upload_url):
    """Upload video using PUT request."""
    async with aiohttp.ClientSession() as session:
        with open(file_path, "rb") as file:
            async with session.put(upload_url, data=file, ssl=ssl_context) as response:
                if response.status == 200:
                    print(f"Successfully uploaded {file_path}")
                    return True
                else:
                    print(f"Failed to upload {file_path}: {response.status}")
                    return False

async def create_post(title, video_url, video_hash):
    """Post video metadata."""
    headers = {"Flic-Token": FLIC_TOKEN, "Content-Type": "application/json"}
    payload = {
        "title": title,
        "hash": video_hash,
        "is_available_in_public_feed": False,
        "category_id": 25,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(POST_URL, json=payload, headers=headers, ssl=ssl_context) as response:
            if response.status in [200, 201]:
                print(f"Post created for {title}")
                return await response.json()
            else:
                print(f"Failed to create post: {response.status}")
                return None

async def upload_videos(downloaded_videos):
    """Handle the upload process for downloaded videos."""
    # Read the set of already uploaded video URLs
    uploaded_urls = read_uploaded_urls()

    for title, file_path, url in downloaded_videos:
        # Skip upload if the video URL has already been uploaded
        if url in uploaded_urls:
            print(f"Skipping already uploaded video: {title}")
            os.remove(file_path)
            continue

        if file_path and os.path.exists(file_path):
            # Fetch the upload URL
            upload_data = await get_upload_url()
            if not upload_data:
                print(f"Failed to get upload URL for {file_path}")
                continue

            # Upload the video
            success = await upload_video(file_path, upload_data["url"])
            if not success:
                print(f"Failed to upload {file_path}")
                continue

            # Create the post with the video hash
            await create_post(title, url, upload_data["hash"])

            # Mark this video as uploaded by saving its URL
            write_uploaded_url(url)

            # Remove the uploaded video from local storage
            os.remove(file_path)
            print(f"Uploaded and removed: {file_path}")
