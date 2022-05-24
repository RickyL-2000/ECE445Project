@echo off & title

for %%a in (*.m4a) do (
 ffmpeg.exe -i "%%~sa" -y -acodec libmp3lame -aq 0 "%%~na.mp3"
)

pause