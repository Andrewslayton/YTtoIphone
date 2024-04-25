import asyncio
import sqlite3
from yt_dlp import YoutubeDL
import os
import youtube_dl
from pytube import YouTube



ydl_opts = {
    'format': 'bestaudio',
    'ignoreerrors': True,
    'verbose': True
}


def dl(url):
    stream = YouTube(url).streams.filter(only_audio=True).first()
    filename = stream.default_filename
    stream.download(filename=filename)

dl('https://www.youtube.com/watch?v=OaQwcXo7tx4&list=PLlu2PoyR1mdFz3zid7F0UrDUMGA6xvS2J&index=4')


