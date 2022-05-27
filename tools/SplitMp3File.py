import os
import re
import sys
import subprocess

# Tool to split a Bible chapter MP3 file into separate verse files.
#
# Usage:
# python -m tools/SplitMp3File.py 40_1.data
#
# Code originally from:
# https://gist.githubusercontent.com/Ashwinning/a9677b5b3afa426667d979b36c019b04
#
# Examples:
#
# python -m tools.SplitMp3File data/40_Matthew001.mp3 data/40_1.data KJV 40 1
# python -m tools.SplitMp3File data/41_Mark001.mp3 data/mal-41-MRK-001.html MOV 41 1
#

codec = '-acodec'

if len(sys.argv) < 6:
    print("Tool to split an MP3 chapter file into verses")
    print("")
    print("Usage:\npython -m tools.SplitMp3File <mp3 filename> <data filename> <bible> <book number> <chapter number>")
    print("")
    print("Example:\npython -m tools.SplitMp3File data/40_Matthew001.mp3 data/40_1.data KJV 40 1")
    print(len(sys.argv))
    exit(0)

mp3file = sys.argv[1]
datafile = sys.argv[2]
bible = sys.argv[3]
book = sys.argv[4]
chapter = sys.argv[5]

if os.path.exists(mp3file):
    print(f"MP3 file: {mp3file}")
else:
    print(f"Cannot find MP3 file: {mp3file}")
    exit(1)

if os.path.exists(datafile):
    print(f"Data file: {datafile}")
else:
    print(f"Cannot find data file: {datafile}")
    exit(1)

print(f"Bible: {bible}")
print(f"Book: {book}")
print(f"Chapter: {chapter}")

tracklist = []

class Track:
    def __init__(self, timestamp, verse):
        self.timestamp = timestamp
        self.verse = verse

class ExtractTracks:
    def __init__(self):
        with open(sys.argv[2], "r") as lines:
            for line in lines:
                # Process { label: "1", start: 3.5, end: 21.05 },
                if ("{" in line) and ("label" in line) and ("start" in line) and ("}" in line):
                    re_data = re.compile('label: "(.*)".*start: (.*?),')
                    se_data = re_data.search(line)
                    verse = se_data.group(1)
                    timestamp = se_data.group(2)
                    # print(f"{verse}:{timestamp}")
                    tracklist.append(Track(timestamp, verse))

def GenerateSplitCommand(start, end, verse):
    directory = f"audio/bibles/{bible}"
    if not os.path.isdir(directory):
        os.mkdir(directory)
    directory = f"{directory}/default"
    if not os.path.isdir(directory):e
        os.mkdir(directory)
    directory = f"{directory}/{book}_{chapter}"
    if not os.path.isdir(directory):
        os.mkdir(directory)
    filename = f"{directory}/{bible}_{book}_{chapter}_{verse}.mp3"
    print(filename)
    return ['ffmpeg', '-i', mp3file, '-ss', start, '-to', end, '-c', 'copy', filename, '-v', 'error']

def GetVideoEnd():
    ffprobeCommand = [
        'ffprobe',
        '-v',
        'error',
        '-show_entries',
        'format=duration',
        '-of',
        'default=noprint_wrappers=1:nokey=1',
        '-sexagesimal',
        mp3file
    ]
    # print(" ".join(ffprobeCommand))
    end = subprocess.check_output(ffprobeCommand).strip()
    return end.decode("utf-8")

ExtractTracks()

for i in range(0, len(tracklist)):
    verse = tracklist[i].verse.strip()
    startTime = tracklist[i].timestamp.strip()
    if i != (len(tracklist) - 1):
        endTime = tracklist[i+1].timestamp.strip() #- startTime
    else:
        endTime = GetVideoEnd() #- startTime
    # print(f"Generating {verse} from {startTime} to {endTime}")
    command = GenerateSplitCommand(str(startTime), str(endTime), verse)
    # print(" ".join(command))
    output = subprocess.check_call(command)
