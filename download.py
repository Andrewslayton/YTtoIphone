import asyncio
import sqlite3
from yt_dlp import YoutubeDL
import os
import youtube_dl
from pytube import YouTube
from tkinter import Tk, Label, Entry, Button, Listbox, END


ydl_opts = {
    'format': 'bestaudio',
    'ignoreerrors': True,
    'verbose': True
}


def dl(url):
    stream = YouTube(url).streams.filter(only_audio=True).first()
    folder = 'downloaded_music'
    filename = stream.default_filename
    stream.download(output_path=folder, filename=filename)



def update_song_list(listbox):
    folder = 'downloaded_music'
    if not os.path.exists(folder):
        os.makedirs(folder)
    listbox.delete(0, END)
    for song in os.listdir('downloaded_music'):
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

root = Tk()
root.geometry("750x600")
root.title("Music download for hypothetical use")

Label(root, text="Enter YouTube URL:").pack()
url_entry = Entry(root, width=100)
url_entry.pack(side = 'top')

download_button = Button(root, text="Download", bg ='yellow', command=lambda: download_and_update(url_entry, song_list))
download_button.pack(padx=10, pady=10)

clear_button = Button(root, text="Clear", bg ='yellow', command=clear_folder)
clear_button.pack(padx=10, pady=10 )

song_list = Listbox(root, width=100, height=30)
song_list.pack()
update_song_list(song_list)


root.mainloop()
