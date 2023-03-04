import config, sys, traceback, os, platform, re
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QRunnable, Slot, Signal, QObject, QThreadPool
else:
    from qtpy.QtCore import QRunnable, Slot, Signal, QObject, QThreadPool
from pydub import AudioSegment
from pydub.playback import play
from util.VlcUtil import VlcUtil


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        #self.kwargs['progress_callback'] = self.signals.progress

    @Slot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class VLCVideo:

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.threadpool = QThreadPool()

    def playVideo(self, videoFilePath, speed):
        VlcUtil.playMediaFile(videoFilePath, speed)
        return "Next ..."

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def workOnPlayVideo(self, videoFilePath, speed):
        # Pass the function to execute
        worker = Worker(self.playVideo, videoFilePath, speed) # Any other args, kwargs are passed to the run function
        worker.signals.finished.connect(self.parent.workOnPlaylistIndex)
        #worker.signals.result.connect(self.print_output)
        #worker.signals.finished.connect(self.thread_complete)
        # Execute
        self.threadpool.start(worker)


class YouTubeDownloader:

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.threadpool = QThreadPool()

    def downloadYouTubeFile(self, downloadCommand, youTubeLink, outputFolder):
        try:
            if platform.system() == "Windows":
                os.system(r"cd .\{2}\ & {0} {1}".format(downloadCommand, youTubeLink, outputFolder))
            else:
                os.system(r"cd {2}; {0} {1}".format(downloadCommand, youTubeLink, outputFolder))
            os.system(r"{0} {1}".format(config.openLinuxDirectory if platform.system() == "Linux" else config.open, outputFolder))
        except:
            self.parent.displayMessage(config.thisTranslation["noSupportedUrlFormat"], title="ERROR:")
            return config.thisTranslation["noSupportedUrlFormat"]
        return "Downloaded!"

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def workOnDownloadYouTubeFile(self, downloadCommand, youTubeLink, outputFolder):
        # Pass the function to execute
        worker = Worker(self.downloadYouTubeFile, downloadCommand, youTubeLink, outputFolder) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.parent.reloadResources)
        # Execute
        self.threadpool.start(worker)

class PydubAudio:

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.threadpool = QThreadPool()

    def pydubFile(self):
        # vlc gui for video only
        config.isMediaPlaying = True
        # Load audio file
        audio = AudioSegment.from_file(config.currentAudioFile, format="mp3")
        # Change speed
        faster_audio = audio.speedup(playback_speed=1.5)
        # Change volume
        louder_audio = faster_audio + 10
        # Play audio
        config.playback = play(louder_audio)

        config.isMediaPlaying = False
        return "Finished Playing!"

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def workOnPydubFile(self):
        # Pass the function to execute
        worker = Worker(self.pydubFile) # Any other args, kwargs are passed to the run function
        #worker.signals.result.connect(self.print_output)
        #worker.signals.finished.connect(self.thread_complete)
        # Execute
        self.threadpool.start(worker)
        
    # stop https://stackoverflow.com/questions/47596007/stop-the-audio-from-playing-in-pydub