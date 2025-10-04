import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import threading
from plyer import notification
from PIL import Image, ImageTk
import urllib.request

# paths to tools
ytdlp = r"bin\yt-dlp.exe"
ffmpeg = r"bin\ffmpeg\bin"
cookies = r"cookies.txt"

# --- version handling ---
def get_local_version():
    try:
        with open(os.path.join("bin", "version.txt"), "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"

def check_update():
    local_version = get_local_version()
    try:
        url = "https://raw.githubusercontent.com/w1zx1/ytdownloader/refs/heads/main/bin/version.txt"
        with urllib.request.urlopen(url) as resp:
            remote_version = resp.read().decode("utf-8").strip()

        if remote_version != local_version:
            messagebox.showinfo("update available",
                                f"a new version is available: {remote_version}\n"
                                f"your version: {local_version}")
        else:
            messagebox.showinfo("up to date",
                                f"you have the latest version: {local_version}")
    except Exception as e:
        messagebox.showerror("update check failed",
                             f"could not check for updates:\n{e}")

# --- notifications ---
def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name='ytdownloader',
        timeout=10
    )

# --- download logic ---
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

# --- format selection handler ---
def on_format_change():
    if format_var.get() == 2:  # mp4
        for widget in quality_frame.winfo_children():
            widget.configure(state=tk.NORMAL)
    else:
        for widget in quality_frame.winfo_children():
            widget.configure(state=tk.DISABLED)
        quality_var.set(0)

# --- gif window ---
def start_gif_window(gif_path, corner="bottom-right", scale=0.4):
    gif_root = tk.Toplevel()
    gif_root.withdraw()  # hide while preparing
    gif_root.overrideredirect(True)
    gif_root.attributes("-topmost", True)

    # load frames
    im = Image.open(gif_path)
    frames, durations = [], []
    try:
        while True:
            frame = im.convert("RGBA")
            if scale != 1.0:
                sz = (int(frame.width * scale), int(frame.height * scale))
                frame = frame.resize(sz, Image.LANCZOS)
            frames.append(ImageTk.PhotoImage(frame, master=gif_root))
            durations.append(im.info.get("duration", 100))
            im.seek(im.tell() + 1)
    except EOFError:
        pass

    label = tk.Label(gif_root, bd=0)
    label.pack()

    w, h = frames[0].width(), frames[0].height()
    sw, sh = gif_root.winfo_screenwidth(), gif_root.winfo_screenheight()
    pad = 10
    taskbar_offset = 50  # move above the taskbar

    if corner == "top-left":
        x, y = pad, pad
    elif corner == "top-right":
        x, y = sw - w - pad, pad
    elif corner == "bottom-left":
        x, y = pad, sh - h - pad - taskbar_offset
    else:  # bottom-right
        x, y = sw - w - pad, sh - h - pad - taskbar_offset

    # set position before showing
    gif_root.geometry(f"{w}x{h}+{x}+{y}")
    gif_root.deiconify()

    idx = 0
    def update():
        nonlocal idx
        label.config(image=frames[idx])
        gif_root.after(durations[idx], update)
        idx = (idx + 1) % len(frames)
    update()

    # close gif window when main root closes
    root.protocol("WM_DELETE_WINDOW", lambda: (root.destroy(), gif_root.destroy()))

# --- center main window ---
def center_window(win, width, height):
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - width) // 2
    y = (sh - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

# --- main gui ---
root = tk.Tk()
root.title("ytdownloader")
center_window(root, 350, 281)

# url input field
tk.Label(root, text="enter your url there").pack(pady=5)
url_entry = tk.Entry(root, width=40)
url_entry.pack(pady=5)

# frame for format and quality selection
selection_frame = tk.Frame(root)
selection_frame.pack(pady=10)

# format selection
format_var = tk.IntVar(value=0)
tk.Label(selection_frame, text="select format:").grid(row=0, column=0, padx=5, sticky=tk.W)
tk.Radiobutton(selection_frame, text="mp3 (audio)", variable=format_var, value=1, command=on_format_change).grid(row=1, column=0, padx=5, sticky=tk.W)
tk.Radiobutton(selection_frame, text="mp4 (video)", variable=format_var, value=2, command=on_format_change).grid(row=2, column=0, padx=5, sticky=tk.W)

# quality selection
quality_frame = tk.Frame(selection_frame)
quality_frame.grid(row=0, column=1, rowspan=3, padx=5)
tk.Label(quality_frame, text="quality of video:").pack(pady=5)
quality_var = tk.IntVar(value=0)
tk.Radiobutton(quality_frame, text="1080p (requires recoding)", variable=quality_var, value=1, state=tk.DISABLED).pack(anchor=tk.W)
tk.Radiobutton(quality_frame, text="720p", variable=quality_var, value=2, state=tk.DISABLED).pack(anchor=tk.W)
tk.Radiobutton(quality_frame, text="480p", variable=quality_var, value=3, state=tk.DISABLED).pack(anchor=tk.W)

# start button
tk.Button(root, text="download", command=download, bg="#4CAF50", fg="white").pack(pady=10)

# update check button
tk.Button(root, text="check for updates", command=check_update, bg="#2196F3", fg="white").pack(pady=5)

# start gif window in parallel
threading.Thread(target=lambda: start_gif_window("bin/animation.gif", "bottom-right", 0.4), daemon=True).start()

root.mainloop()
