import os, sys
from pydub import AudioSegment
from pydub.playback import play


class PydubUtil:

    @staticmethod
    def exportAudioFile(audioFile, speed, speedUpFilterFrequency, exportPath=""):
        audioSegment = PydubUtil.audioChangeSpeed(audioFile, speed, speedUpFilterFrequency)
        if not exportPath:
            exportPath = os.path.join("temp", "pydub.wav")
        if os.path.isfile(exportPath):
            os.remove(exportPath)
        audioSegment.export(exportPath, format="wav")
        return os.path.abspath(exportPath)

    @staticmethod
    def audioChangeSpeed(audioFile, speed, speedUpFilterFrequency):
        #audioFile = os.path.abspath(audioFile)
        fileExtension = os.path.splitext(audioFile)[-1][1:]
        audioSegment = AudioSegment.from_file(audioFile, format=fileExtension)
        # limit speed to 0.25 <= speed <= 2.0
        speed = float(speed)
        if speed > 2.0:
            speed = 2.0
        elif speed < 0.25:
            speed = 0.25
        # modify speed if speed is not equal to 1.0
        # use different approaches for changing speed
        if speed > 1.0:
            return PydubUtil.audioSpeedUp(audioSegment, speed, speedUpFilterFrequency)
        elif speed < 1.0:
            return PydubUtil.audioSlowDown(audioSegment, speed)
        # without changing
        return audioSegment

    @staticmethod
    def audioSpeedUp(audioSegment, speed, speedUpFilterFrequency):
        # return modified audio segment
        #return audioSegment.speedup(playback_speed=speed)
        # alternately, use high_pass_filter and low_pass_filter to wrap the speedup, to perserve the pitch better
        audioSegment = audioSegment.high_pass_filter(speedUpFilterFrequency).speedup(playback_speed=speed, chunk_size=150, crossfade=25).low_pass_filter(speedUpFilterFrequency)
        # increase volume by 12dB
        return (audioSegment + 15)

    @staticmethod
    def audioSlowDown(audioSegment, speed):
        # return modified audio segment
        # alternately, use _data instead of raw_data, no difference noted
        slow_audio = audioSegment._spawn(audioSegment.raw_data, overrides={"frame_rate": int(audioSegment.frame_rate * speed)})
        # try to perserve better pitch quality by using the original frame rate
        return slow_audio.set_frame_rate(audioSegment.frame_rate)


if __name__ == '__main__':
    # run this block of script as a subprocess to hide pydub print output while audio is playing
    speed = float(sys.argv[1])
    speedUpFilterFrequency = int(sys.argv[2])
    audioFile = " ".join(sys.argv[3:])
    play(PydubUtil.audioChangeSpeed(audioFile, speed, speedUpFilterFrequency))
    isPydubPlaying = os.path.join("temp", "isPydubPlaying")
    if os.path.isfile(isPydubPlaying):
        os.remove(isPydubPlaying)
