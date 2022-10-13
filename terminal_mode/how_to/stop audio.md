# How to Stop Audio Playing

In most cases, you can stop audio playing by running:

> .stopaudio

However, '.stopaudio' command does not work in the following two cases:

1) use .readsync or readsync::: command to play audio with text synchronisation, 

2) use Android built-in Google text-to-speech with Termux:API app termux-tts-speak command

To stop audio in these two cases:

1) Launch a file manager
2) Open the "temp" folder in UniqueBible home directory, i.e. UniqueBible/temp/
3) Delete the file "000_audio_playing.txt"
