import numpy as np
import struct

class WaveHandler():
    def __init__(self):
        self.audioData = []
        self.loaded = False
        self.samplerate = 0
        self.noofframes = 0

    def gettotaltime(self):
        if self.loaded:
            return round(self.noofframes / self.samplerate, 2)
        else:
            return 0.00

    def framestoseconds(self, framecount):
        if self.loaded:
            return round(framecount / self.samplerate, 2)
        else:
            return 0.00

    def getdrawpoints(self, datastart):
        N = 1024
        pointlist = []
        for x in range(-256, 768):
            index = (x * 4) + datastart
            if(index < 0) or (index >= (len(self.audioData) - 1)) or\
                    (len(self.audioData) == 0):
                pointlist.append(256)
            else:
                pointlist.append((self.audioData[index]/128)+256)
        return pointlist

    def getaudiodata(self, datastart, scale, sector):
        #assumes there is data loaded
        #2048 16bit signed bits
        #!!!THIS NEEDS PADDING AND FILTERING AS WILL BE PLAYING BACK AT FREQUENCY
        #Will div 128
        audiolist = []
        for x in range(0, 2048):
            audiolist.append(self.audioData[x + datastart])
        return audiolist

    def loadwave(self, file):
        self.samplerate = file.getframerate()
        self.noofframes = file.getnframes()
        self.loaded = True
        wavData = file.readframes(file.getnframes())
        self.audioData = struct.unpack("%ih" % file.getnframes()
                                            * file.getnchannels(), wavData)
