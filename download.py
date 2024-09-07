import os
import shutil
from tkinter import Tk, Label, Entry, Button, Listbox, END
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from youtubesearchpython import VideosSearch

ydl_opts = {
    'format': 'bestaudio/best',
    'ignoreerrors': True,
    'verbose': True,
    'outtmpl': 'downloaded_music/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'postprocessor_args': [
        '-ar', '44100'
    ],
    'prefer_ffmpeg': True,
    'keepvideo': False
}

def search_and_download(query):
    videos_search = VideosSearch(query, limit=1)
    result = videos_search.result()
    if result['result']:
        url = result['result'][0]['link']
        return dl(url)
    else:
        print(f"No results found for {query}")
        return None

def dl(url):
    folder = 'downloaded_music'
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    with YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(result).replace('.webm', '.mp3').replace('.m4a', '.mp3')
        except DownloadError as e:
            print(f"Error downloading {url}: {e}")
            return None

def download_and_update(url_entry, song_list):
    query = url_entry.get()
    if query.startswith("http"):
        file_name = dl(query)
    else:
        file_name = search_and_download(query)
    
    if file_name:
        song_list.insert(END, os.path.basename(file_name))

def add_to_itunes():
    folder = 'downloaded_music'
    music_path = os.path.join(os.environ['USERPROFILE'], 'Music')
    itunes_auto_add_folder = os.path.join(music_path, 'iTunes', 'iTunes Media', 'Automatically Add to iTunes')
    if not os.path.exists(itunes_auto_add_folder):
        os.makedirs(itunes_auto_add_folder)
        print(f"Created iTunes auto-add folder at {itunes_auto_add_folder}")
    for song in os.listdir(folder):
        source_path = os.path.join(folder, song)
        destination_path = os.path.join(itunes_auto_add_folder, song)
        if os.path.exists(source_path):
            shutil.move(source_path, destination_path)
            print(f"Moved to iTunes auto-add folder: {destination_path}")
        else:
            print(f"File not found: {source_path}")

root = Tk()
root.geometry("750x600")
root.title("Music Download for Hypothetical Use")

Label(root, text="YouTube URL or Song Name:").grid(row=0, column=0)
url_entry = Entry(root, width=50)
url_entry.grid(row=0, column=1)

download_button = Button(root, text="Download", bg='yellow', command=lambda: download_and_update(url_entry, song_list))
download_button.grid(row=0, column=2)

itunes_button = Button(root, text="Add to iTunes", bg='lightblue', command=add_to_itunes)
itunes_button.grid(row=0, column=3)

song_list = Listbox(root, width=100)
song_list.grid(row=1, column=0, columnspan=4)

root.mainloop()