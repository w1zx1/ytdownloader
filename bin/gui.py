import tkinter as tk
from tkinter import messagebox
import subprocess
import os
from plyer import notification

# paths to tools
ytdlp = r"bin\yt-dlp.exe"
ffmpeg = r"bin\ffmpeg\bin"
cookies = r"cookies.txt"

def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name='ytdownloader',
        timeout=10
    )

def download():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("error", "enter url of the video!")
        return

    fmt = format_var.get()
    if fmt == 0:
        messagebox.showwarning("error", "select format (mp3 or mp4)!")
        return

    print("starting to download...")

    if fmt == 1:  # mp3
        cmd = [
            ytdlp,
            "--cookies", cookies,
            "--ffmpeg-location", ffmpeg,
            "-x", "--audio-format", "mp3",
            url
        ]
    else:  # mp4
        quality = quality_var.get()
        if quality == 0:
            messagebox.showwarning("error", "select quality of video!")
            return

        if quality == 1:
            format_str = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
            cmd = [
                ytdlp,
                "--cookies", cookies,
                "--ffmpeg-location", ffmpeg,
                "-f", format_str,
                "--recode-video", "mp4",
                url
            ]
        elif quality == 2:
            format_str = 'best[ext=mp4][height<=720]'
            cmd = [
                ytdlp,
                "--cookies", cookies,
                "--ffmpeg-location", ffmpeg,
                "-f", format_str,
                url
            ]
        elif quality == 3:
            format_str = 'best[ext=mp4][height<=480]'
            cmd = [
                ytdlp,
                "--cookies", cookies,
                "--ffmpeg-location", ffmpeg,
                "-f", format_str,
                url
            ]

    try:
        subprocess.run(cmd, check=True)
        print("download completed!")
        show_notification("ytdownloader", "download completed!")
    except subprocess.CalledProcessError as e:
        print("error executing download")
        show_notification("ytdownloader", f"download error: {e}")

def on_format_change():
    if format_var.get() == 2:  # mp4
        for widget in quality_frame.winfo_children():
            widget.configure(state=tk.NORMAL)
    else:
        for widget in quality_frame.winfo_children():
            widget.configure(state=tk.DISABLED)
        quality_var.set(0)

# --- gui ---
root = tk.Tk()
root.title("ytdownloader")
root.geometry("350x245")

# url input field
tk.Label(root, text="enter your url there").pack(pady=5)
url_entry = tk.Entry(root, width=40)
url_entry.pack(pady=5)

# frame for format and quality selection
selection_frame = tk.Frame(root)
selection_frame.pack(pady=10)

# format selection on the left
format_var = tk.IntVar(value=0)
tk.Label(selection_frame, text="select format:").grid(row=0, column=0, padx=5, sticky=tk.W)
tk.Radiobutton(selection_frame, text="mp3 (audio)", variable=format_var, value=1, command=on_format_change).grid(row=1, column=0, padx=5, sticky=tk.W)
tk.Radiobutton(selection_frame, text="mp4 (video)", variable=format_var, value=2, command=on_format_change).grid(row=2, column=0, padx=5, sticky=tk.W)

# quality selection on the right (initially disabled)
quality_frame = tk.Frame(selection_frame)
quality_frame.grid(row=0, column=1, rowspan=3, padx=5)
tk.Label(quality_frame, text="quality of video:").pack(pady=5)
quality_var = tk.IntVar(value=0)
tk.Radiobutton(quality_frame, text="1080p (requires recoding)", variable=quality_var, value=1, state=tk.DISABLED).pack(anchor=tk.W)
tk.Radiobutton(quality_frame, text="720p", variable=quality_var, value=2, state=tk.DISABLED).pack(anchor=tk.W)
tk.Radiobutton(quality_frame, text="480p", variable=quality_var, value=3, state=tk.DISABLED).pack(anchor=tk.W)

# start button
tk.Button(root, text="download", command=download, bg="#4CAF50", fg="white").pack(pady=10)

root.mainloop()
