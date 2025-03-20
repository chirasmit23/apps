import streamlit as st
import yt_dlp
import os
import uuid

# Set the downloads folder
DOWNLOADS_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)

# Video download function
def download_video(post_url, quality="best"):
    unique_filename = f"video_{uuid.uuid4().hex}.mp4"
    video_path = os.path.join(DOWNLOADS_FOLDER, unique_filename)

    quality_formats = {
        "1080": "bestvideo[height<=1080]+bestaudio/best",
        "720": "bestvideo[height<=720]+bestaudio/best",
        "480": "bestvideo[height<=480]+bestaudio/best",
        "best": "bestvideo+bestaudio/best"
    }
    video_format = quality_formats.get(quality, "bestvideo+bestaudio/best")

    ydl_opts = {
        "format": video_format,
        "outtmpl": video_path,
        "merge_output_format": "mp4",
        "quiet": True,
        "http_headers": {"User-Agent": "Mozilla/5.0"}
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([post_url])
        return video_path
    except Exception as e:
        st.error(f"Download Error: {e}")
        return None

# Streamlit UI
st.title("📥 Video Downloader")
st.write("Download videos from various platforms by providing a URL.")

video_url = st.text_input("Enter video URL:")
resolution = st.selectbox("Select Resolution:", ["360p", "480p", "720p", "1080p", "best"], index=4)

if st.button("Download Video"):
    if video_url:
        st.info("Downloading... Please wait.")
        file_path = download_video(video_url, resolution)
        if file_path:
            st.success("Download complete!")
            with open(file_path, "rb") as file:
                st.download_button(label="Click here to download", data=file, file_name=os.path.basename(file_path), mime="video/mp4")
        else:
            st.error("Failed to download video.")
    else:
        st.warning("Please enter a valid URL!")
