import asyncio
import sqlite3
import time
from yt_dlp import YoutubeDL
import os
import shutil
from pytube import YouTube, Playlist
from tkinter import Tk, Label, Entry, Button, Listbox, END

ydl_opts = {
    'format': 'bestaudio',
    'ignoreerrors': True,
    'verbose': True
}

def dl(url):
    folder = 'downloaded_music'
    if 'playlist' in url:
        playlist = Playlist(url)
        for video in playlist.videos:
            stream = video.streams.filter(only_audio=True).first()
            filename = stream.default_filename
            stream.download(output_path=folder, filename=filename)
            time.sleep(5)
    else: 
        stream = YouTube(url).streams.filter(only_audio=True).first()
        filename = stream.default_filename
        stream.download(output_path=folder, filename=filename)

def update_song_list(listbox):
    folder = 'downloaded_music'
    if not os.path.exists(folder):
        os.makedirs(folder)
    listbox.delete(0, END)
    for song in os.listdir(folder):
        listbox.insert(END, song)

def download_and_update(url_entry, listbox):
    url = url_entry.get()
    dl(url)
    url_entry.delete(0, 'end')
    update_song_list(listbox)

def clear_folder():
    folder = 'downloaded_music'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    update_song_list(song_list)

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

Label(root, text="Enter YouTube URL if its a playlist be patient it takes a while").pack()
url_entry = Entry(root, width=100)
url_entry.pack(side='top')

download_button = Button(root, text="Download", bg='yellow', command=lambda: download_and_update(url_entry, song_list))
download_button.pack(padx=10, pady=10)

clear_button = Button(root, text="Clear", bg='yellow', command=clear_folder)
clear_button.pack(padx=10, pady=10)

itunes_button = Button(root, text="Add to iTunes", bg='green', command=add_to_itunes)
itunes_button.pack(padx=10, pady=10)

song_list = Listbox(root, width=100, height=30)
song_list.pack()
update_song_list(song_list)

root.mainloop()
