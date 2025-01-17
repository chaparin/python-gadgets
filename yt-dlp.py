import yt_dlp

# Define the video URL
video_url = "https://www.youtube.com/watch?v=eNoqKODqMn8"  # Replace with the actual YouTube video URL

# Set options to download the highest quality single format available
ydl_opts = {
    'format': 'best',  # Downloads the best available format with both video and audio
}

# Use yt_dlp to download the video
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([video_url])
