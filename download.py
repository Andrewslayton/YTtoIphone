import os
import shutil
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

DOWNLOAD_FOLDER = "downloaded_music"
COOKIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")

YDL_OPTS = {
    "format": "bestaudio/best",
    "ignoreerrors": True,
    "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
    "postprocessor_args": ["-ar", "44100"],
    "prefer_ffmpeg": True,
    "keepvideo": False,
    "quiet": True,
    "no_warnings": True,
}

if os.path.isfile(COOKIES_FILE):
    YDL_OPTS["cookiefile"] = COOKIES_FILE

BG = "#1e1e2e"
BG_SECONDARY = "#2a2a3c"
FG = "#cdd6f4"
FG_DIM = "#6c7086"
ACCENT = "#89b4fa"
GREEN = "#a6e3a1"
RED = "#f38ba8"
YELLOW = "#f9e2af"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YT to iPhone")
        self.geometry("720x520")
        self.minsize(580, 420)
        self.configure(bg=BG)
        self.resizable(True, True)

        self._style_widgets()
        self._build_ui()
        self._refresh_song_list()

    def _style_widgets(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(".", background=BG, foreground=FG)
        style.configure("TFrame", background=BG)
        style.configure("Secondary.TFrame", background=BG_SECONDARY)
        style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))
        style.configure(
            "Header.TLabel",
            background=BG,
            foreground=FG,
            font=("Segoe UI", 20, "bold"),
        )
        style.configure(
            "Section.TLabel",
            background=BG_SECONDARY,
            foreground=FG,
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "Status.TLabel",
            background=BG_SECONDARY,
            foreground=FG_DIM,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Accent.TButton",
            background=ACCENT,
            foreground="#1e1e2e",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 8),
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#74a8f7"), ("disabled", "#45475a")],
            foreground=[("disabled", "#6c7086")],
        )
        style.configure(
            "Green.TButton",
            background=GREEN,
            foreground="#1e1e2e",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 8),
        )
        style.map("Green.TButton", background=[("active", "#8bd89a")])
        style.configure(
            "Red.TButton",
            background=RED,
            foreground="#1e1e2e",
            font=("Segoe UI", 10),
            padding=(12, 8),
        )
        style.map("Red.TButton", background=[("active", "#e67a96")])

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # --- Header ---
        header = ttk.Label(self, text="YT to iPhone", style="Header.TLabel")
        header.grid(row=0, column=0, pady=(18, 4), padx=24, sticky="w")

        # --- Input area ---
        input_frame = ttk.Frame(self, style="Secondary.TFrame")
        input_frame.grid(row=1, column=0, padx=24, pady=(8, 4), sticky="ew")
        input_frame.columnconfigure(0, weight=1)

        self.entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 11),
            bg="#313244",
            fg=FG,
            insertbackground=FG,
            relief="flat",
            highlightthickness=2,
            highlightcolor=ACCENT,
            highlightbackground="#45475a",
        )
        self.entry.grid(row=0, column=0, padx=(12, 8), pady=12, sticky="ew")
        self.entry.bind("<Return>", lambda _: self._start_download())
        self._set_placeholder()
        self.entry.bind("<FocusIn>", self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._restore_placeholder)

        self.dl_button = ttk.Button(
            input_frame,
            text="Download",
            style="Accent.TButton",
            command=self._start_download,
        )
        self.dl_button.grid(row=0, column=1, padx=(0, 12), pady=12)

        # --- Song list ---
        list_frame = ttk.Frame(self, style="Secondary.TFrame")
        list_frame.grid(row=2, column=0, padx=24, pady=8, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)

        ttk.Label(list_frame, text="Downloaded Songs", style="Section.TLabel").grid(
            row=0, column=0, padx=12, pady=(10, 0), sticky="w"
        )

        self.listbox = tk.Listbox(
            list_frame,
            font=("Segoe UI", 10),
            bg="#313244",
            fg=FG,
            selectbackground=ACCENT,
            selectforeground="#1e1e2e",
            relief="flat",
            highlightthickness=0,
            activestyle="none",
            borderwidth=0,
        )
        self.listbox.grid(row=1, column=0, padx=12, pady=(6, 12), sticky="nsew")

        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.listbox.yview
        )
        scrollbar.grid(row=1, column=1, pady=(6, 12), sticky="ns")
        self.listbox.configure(yscrollcommand=scrollbar.set)

        # --- Bottom bar ---
        bottom = ttk.Frame(self, style="Secondary.TFrame")
        bottom.grid(row=3, column=0, padx=24, pady=(0, 18), sticky="ew")
        bottom.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            bottom, textvariable=self.status_var, style="Status.TLabel"
        )
        self.status_label.grid(row=0, column=0, padx=12, pady=10, sticky="w")

        self.itunes_btn = ttk.Button(
            bottom,
            text="Add to iTunes",
            style="Green.TButton",
            command=self._add_to_itunes,
        )
        self.itunes_btn.grid(row=0, column=1, padx=(0, 6), pady=10)

        self.clear_btn = ttk.Button(
            bottom,
            text="Clear",
            style="Red.TButton",
            command=self._clear_downloads,
        )
        self.clear_btn.grid(row=0, column=2, padx=(0, 12), pady=10)

    # --- Placeholder logic ---

    def _set_placeholder(self):
        self.entry.insert(0, "Paste a YouTube URL or type a song name...")
        self.entry.configure(fg=FG_DIM)
        self._placeholder_active = True

    def _clear_placeholder(self, _event=None):
        if self._placeholder_active:
            self.entry.delete(0, "end")
            self.entry.configure(fg=FG)
            self._placeholder_active = False

    def _restore_placeholder(self, _event=None):
        if not self.entry.get().strip():
            self._set_placeholder()

    # --- Status helpers ---

    def _set_status(self, text, color=FG_DIM):
        self.status_var.set(text)
        self.status_label.configure(foreground=color)

    def _set_busy(self, busy):
        state = "disabled" if busy else "normal"
        self.dl_button.configure(state=state)
        self.entry.configure(state=state)

    # --- Download ---

    def _start_download(self):
        query = self.entry.get().strip()
        if not query or self._placeholder_active:
            self._set_status("Enter a URL or song name first", RED)
            return

        self._set_busy(True)
        self._set_status("Searching and downloading...", YELLOW)
        threading.Thread(target=self._download_worker, args=(query,), daemon=True).start()

    def _download_worker(self, query):
        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
        url = query if query.startswith("http") else f"ytsearch:{query}"

        try:
            with YoutubeDL(YDL_OPTS) as ydl:
                result = ydl.extract_info(url, download=True)
                if result and result.get("_type") == "playlist":
                    entries = result.get("entries") or []
                    result = next((e for e in entries if e), None)

                if result:
                    title = result.get("title", "Unknown")
                    self.after(0, self._on_success, title)
                else:
                    self.after(0, self._on_fail, "No results found")
        except DownloadError as e:
            self.after(0, self._on_fail, str(e)[:100])
        except Exception as e:
            self.after(0, self._on_fail, str(e)[:100])

    def _on_success(self, title):
        self._set_busy(False)
        self._set_status(f"Downloaded: {title}", GREEN)
        self.entry.delete(0, "end")
        self._refresh_song_list()

    def _on_fail(self, error):
        self._set_busy(False)
        self._set_status(f"Error: {error}", RED)

    # --- Song list management ---

    def _refresh_song_list(self):
        self.listbox.delete(0, "end")
        if os.path.exists(DOWNLOAD_FOLDER):
            songs = sorted(f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith(".mp3"))
            for song in songs:
                self.listbox.insert("end", f"  {os.path.splitext(song)[0]}")
        if self.listbox.size() == 0:
            self.listbox.insert("end", "  No songs yet — download something!")

    # --- iTunes ---

    def _add_to_itunes(self):
        if not os.path.exists(DOWNLOAD_FOLDER):
            self._set_status("Nothing to add", RED)
            return

        songs = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith(".mp3")]
        if not songs:
            self._set_status("No songs to add", RED)
            return

        music_path = os.path.join(os.environ.get("USERPROFILE", ""), "Music")
        itunes_folder = os.path.join(
            music_path, "iTunes", "iTunes Media", "Automatically Add to iTunes"
        )
        os.makedirs(itunes_folder, exist_ok=True)

        moved = 0
        for song in songs:
            try:
                shutil.move(
                    os.path.join(DOWNLOAD_FOLDER, song),
                    os.path.join(itunes_folder, song),
                )
                moved += 1
            except OSError:
                pass

        self._set_status(f"Moved {moved} song(s) to iTunes", GREEN)
        self._refresh_song_list()

    # --- Clear ---

    def _clear_downloads(self):
        if not os.path.exists(DOWNLOAD_FOLDER):
            return
        files = os.listdir(DOWNLOAD_FOLDER)
        if not files:
            return
        if not messagebox.askyesno("Confirm", f"Delete {len(files)} file(s)?"):
            return
        for f in files:
            try:
                os.remove(os.path.join(DOWNLOAD_FOLDER, f))
            except OSError:
                pass
        self._set_status("Downloads cleared", FG_DIM)
        self._refresh_song_list()


if __name__ == "__main__":
    App().mainloop()
