# How to Stop Audio Playing

In most cases, you can stop audio playing by running:

> .stopaudio

However, '.stopaudio' command does not stop audio playing with text synchronisation, which can be run with:

* .readsync command
* readsync::: command keyword
* .tts command on Android termux

To stop audio with text synchronisation, run the following command in UBA running in a separate session:

> .stopaudiosync

As the audio playing with text synchronisation occupies the running session, you need to open UBA in an additional session to run the command above.

Alternately, you can also manually do the following steps:

1) Launch a file manager
2) Open the "temp" folder in UniqueBible home directory, i.e. UniqueBible/temp/
3) Delete the file "000_audio_playing.txt"

Remarks: Stoping audio playing with text synchronisation does not bring immediate stop to audio playing.  Instead, it breaks the loop of alternate text display and audio playing.  The audio stops when reading the currently displayed text is finished. 
