import os, config
from pydub import AudioSegment


class MediaUtil:

    # for testing audioFile = "/Users/office/uniquebibleapp-webtop/UniqueBible/audio/bibles/NET/default/1_1/NET_1_1_1.mp3"

    @staticmethod
    def audioChangeSpeed(audioFile, speed):
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
            return MediaUtil.audioSpeedUp(audioSegment, speed)
        elif speed < 1.0:
            return MediaUtil.audioSlowDown(audioSegment, speed)
        # without changing
        return audioSegment

    @staticmethod
    def audioSpeedUp(audioSegment, speed):
        # return modified audio segment
        #return audioSegment.speedup(playback_speed=speed)
        # alternately, use high_pass_filter and low_pass_filter to wrap the speedup, to perserve the pitch better
        return audioSegment.high_pass_filter(config.speedUpFilterFrequency).speedup(playback_speed=speed).low_pass_filter(config.speedUpFilterFrequency)

    @staticmethod
    def audioSlowDown(audioSegment, speed):
        # return modified audio segment
        # alternately, use _data instead of raw_data, no difference noted
        slow_audio = audioSegment._spawn(audioSegment.raw_data, overrides={"frame_rate": int(audioSegment.frame_rate * speed)})
        # try to perserve better pitch quality by using the original frame rate
        return slow_audio.set_frame_rate(audioSegment.frame_rate)