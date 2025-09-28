@echo off
set /p url=enter url to download: 

echo choose format:
echo 1 - MP3 (audio only)
echo 2 - MP4 (video)
set /p format_choice=enter choice (1-2): 

if "%format_choice%"=="1" (
    echo extracting audio as MP3...
    bin\yt-dlp.exe --cookies "cookies.txt" --ffmpeg-location "bin\ffmpeg\bin" -x --audio-format mp3 %url%
    set result=%errorlevel%
    goto check_result
) else if "%format_choice%"=="2" (
    echo choose quality:
    echo 1 - 1080p (will require recoding, which will take 100%% of your cpu)
    echo 2 - 720p
    echo 3 - 480p
    set /p quality_choice=enter choice (1-3): 

    if "%quality_choice%"=="1" set format="bestvideo[height<=1080]+bestaudio/best[height<=1080]" --recode-video mp4
    if "%quality_choice%"=="2" set format="best[ext=mp4][height<=720]"
    if "%quality_choice%"=="3" set format="best[ext=mp4][height<=480]"

    bin\yt-dlp.exe --cookies "cookies.txt" --ffmpeg-location "bin\ffmpeg\bin" -f %format% %url%
    set result=%errorlevel%
    goto check_result
)

:check_result
if %result%==0 (
    powershell -command "add-type -assemblyname system.windows.forms; [system.windows.forms.messagebox]::show('ytdownloader: done downloading!') | Out-Null"
) else (
    powershell -command "add-type -assemblyname system.windows.forms; [system.windows.forms.messagebox]::show('ytdownloader: download failed! check console for details') | Out-Null"
)

pause
