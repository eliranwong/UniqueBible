# Folder "music"
Youtube files download via UniqueBible.app are converted to mp3 and placed in this folder

# Latest changes in version 10.9:
* Added support of using youtube-dl on Windows, macOS & Linux
* This feature downloads a video file from a youtube link user provides, convert it into a mp3 file and saved in folder "music" inside "UniqueBible" folder.
* Users need to install youtube-dl and ffmpeg before they can run this feature.
* Read: http://ytdl-org.github.io/youtube-dl/download.html for details on downloading youtube-dl
* Below are the methods we tested to download youtube-dl and ffmpeg:

    [on Linux]<br>
    - Run in terminal:<br>
    > sudo curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl<br>
    > sudo chmod a+rx /usr/local/bin/youtube-dl<br>
    > sudo apt install ffmpeg<br>

    [on Windows]<br>
    - Install "chocolatey" first. read https://chocolatey.org/install<br>
    - open Windows PowerShell (Admin), and run:<br>
    > choco install youtube-dl<br>
    > choco install ffmpeg<br>

    [on macOS]<br>
    - Install "homebrew" first. read https://brew.sh/<br>
    - Run in terminal:<br>
    > brew install youtube-dl<br>
    > brew install ffmpeg<br>

* To use keyword in UniqueBible.app "mp3:::[a_youtube_link]", enter in command line field, e.g.
    > mp3:::https://www.youtube.com/watch?v=CDdvReNKKuk
* To use a graphical dialog box to run this feature in UniqueBible.app,
    - Select from menu "Resources > YouTube -> mp3"
    - Enter a link, e.g. https://www.youtube.com/watch?v=CDdvReNKKuk
    - Select "OK"
