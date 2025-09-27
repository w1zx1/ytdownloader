@echo off
set /p url=enter url to download: 

echo choose quality:
echo 1 - 1080p (will require recoding, which will take 100% of your cpu)
echo 2 - 720p
echo 3 - 480p
set /p quality_choice=enter choice (1-3): 

if "%quality_choice%"=="1" set format="bestvideo[height<=1080]+bestaudio/best[height<=1080]" --recode-video mp4
if "%quality_choice%"=="2" set format="best[ext=mp4][height<=720]"
if "%quality_choice%"=="3" set format="best[ext=mp4][height<=480]"

bin\yt-dlp.exe --cookies "bin\cookies.txt" --ffmpeg-location "bin\ffmpeg\bin" -f %format% %url%
set result=%errorlevel%

if %result%==0 (
    powershell -command "add-type -assemblyname system.windows.forms; [system.windows.forms.messagebox]::show('done!') | Out-Null"
) else (
    powershell -command "add-type -assemblyname system.windows.forms; [system.windows.forms.messagebox]::show('failed! check console for details') | Out-Null"
)

pause
