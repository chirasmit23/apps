from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import uuid
import time
import random
import requests
from threading import Thread
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivy.clock import mainthread

# Initialize Flask App
app = Flask(__name__)
DOWNLOADS_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)  # Ensure download folder exists

# Video Download Function
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
        "http_headers": {
            "User-Agent": "Mozilla/5.0"
        }
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([post_url])
        return video_path
    except Exception as e:
        print(f"Download Error: {e}")
        return None

@app.route("/video", methods=["POST"])
def video_downloader():
    video_url = request.form.get("video_url")
    quality = request.form.get("quality", "best")

    if video_url:
        file_path = download_video(video_url, quality)
        if file_path:
            return send_file(file_path, as_attachment=True)
        else:
            return "Error: Video could not be downloaded.", 500
    return "Invalid Request", 400

# Start Flask in a separate thread
def start_flask():
    app.run(host="0.0.0.0", port=10000, debug=False, use_reloader=False)

flask_thread = Thread(target=start_flask, daemon=True)
flask_thread.start()

# Kivy UI
KV = """
ScreenManager:
    HomeScreen:

<HomeScreen>:
    name: "home"
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(15)
        pos_hint: {"center_x": 0.5, "center_y": 0.5}

        MDLabel:
            text: "Video Downloader"
            theme_text_color: "Primary"
            font_style: "H5"
            halign: "center"

        MDTextField:
            id: url_input
            hint_text: "Enter video URL"
            size_hint_x: None
            width: dp(300)
            pos_hint: {"center_x": 0.5}

        MDRaisedButton:
            text: "Select Resolution"
            size_hint_x: None
            width: dp(200)
            pos_hint: {"center_x": 0.5}
            on_release: app.show_resolution_menu()

        MDLabel:
            id: resolution_label
            text: "Selected Resolution: None"
            theme_text_color: "Secondary"
            halign: "center"

        MDRaisedButton:
            text: "Download"
            size_hint_x: None
            width: dp(200)
            pos_hint: {"center_x": 0.5}
            on_release: app.download_video()
"""

class HomeScreen(Screen):
    pass

class VideoDownloaderApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.resolutions = ["360p", "480p", "720p", "1080p", "4K"]
        return Builder.load_string(KV)

    def show_resolution_menu(self):
        home_screen = self.root.get_screen("home")
        menu_items = [
            {
                "text": res,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=res: self.set_resolution(x),
            }
            for res in self.resolutions
        ]
        self.menu = MDDropdownMenu(
            caller=home_screen.ids.url_input,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def set_resolution(self, resolution):
        home_screen = self.root.get_screen("home")
        home_screen.ids.resolution_label.text = f"Selected Resolution: {resolution}"
        self.menu.dismiss()

    @mainthread
    def download_video(self):
        home_screen = self.root.get_screen("home")
        url = home_screen.ids.url_input.text
        resolution = home_screen.ids.resolution_label.text.replace("Selected Resolution: ", "")
        
        if not url or resolution == "None":
            print("Error: Please enter a URL and select a resolution!")
            return
        
        print(f"Downloading {url} in {resolution}...")
        response = requests.post("http://127.0.0.1:10000/video", data={"video_url": url, "quality": resolution})
        
        if response.status_code == 200:
            print("Download successful!")
        else:
            print("Error downloading video.")

if __name__ == "__main__":
    VideoDownloaderApp().run()