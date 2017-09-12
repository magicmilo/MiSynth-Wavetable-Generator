#!/usr/bin/env python3
"""
Plays back and handles wave samples
Gets 2048 samples from main application
Plays back chunks of this at the selected frequency
e.g 128 of 2048 samples
sample[960:1088] played back at 440Hz would require a samplerate of 56320Hz
roughly equivalent to the 44100Hz sound card default
the centre point can be shifted

Chunk size can be changed based on original file samplerate to match frequence
Output to file will have smoothing function
The smoothed file will retain frequency characteristics and then will
be playable with this (chunk length 2048)

"""
import queue
import sys
import threading
import numpy as np
import sounddevice as sd

class AudioHandler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.proccount = 0
        self.active = False
        self.frequency = 400
        self.counter = 0
        self.step = 1
        self.shift = 960
        self.chunklength = 128
        self.sample = []

        self.settings = {'device': 10,
                    'channels': 1,
                    'samplerate': 44100,
                    'blocksize': 2048,
                    'buffersize': 512}

        self.q = queue.Queue(maxsize=self.settings['buffersize'])
        self.event = threading.Event()
        self.stream = sd.OutputStream(
            samplerate=self.settings['samplerate'],
            blocksize=self.settings['blocksize'],
            device=sd.default.device,
            channels=self.settings['channels'],
            dtype='int16',
            callback=self.callback,
            finished_callback=self.event.set)

    def run(self):
        self.active = True
        try:
            #print(sd.query_devices())
            data = self.getblock()
            self.q.put_nowait(data)  # Pre-fill queue

            with self.stream:
                timeout = (self.settings['blocksize']
                          * self.settings['buffersize']
                          / self.settings['samplerate'])
                while self.active:
                    data = self.getblock()
                    self.q.put(data, timeout=timeout)
                #self.event.wait()
        except queue.Full:
            # A timeout occured, i.e. there was an error in the callback
            print("Queue Full")
        except Exception as e:
            print("Exception " + str(e))
        return

    def setsample(self, sample, length):
        assert len(sample) == length
        assert length == 2048
        self.step = self.chunklength * self.frequency / self.settings["samplerate"]
        assert self.step < self.chunklength
        self.sample = sample

    def stop(self):
        print("Stopping")
        self.stream.stop()
        self.active = False

    def callback(self, outdata, frames, time, status):
        assert frames == self.settings['blocksize']
        if status.output_underflow:
            print('Output underflow: increase blocksize?', file=sys.stderr)
            raise sd.CallbackAbort
        assert not status
        try:
            data = self.q.get_nowait()
        except queue.Empty:
            print('Buffer is empty: increase buffersize?', file=sys.stderr)
            raise sd.CallbackAbort

        if len(data) < len(outdata):
            outdata[:len(data)] = data
            outdata[len(data):] = b'\x00' * (len(outdata) - len(data))
            raise sd.CallbackStop
        else:
            outdata[:] = data

    def getblock(self):
        if len(self.sample) == 0:
            block = self.gettestblock()
        else:
            block = self.getsampleblock()
        x = np.array(block, dtype='int16')
        x.shape = (2048, 1)
        return x

    def getsampleblock(self):
        block = []
        for cnt in range(0, 2048):
            s = self.sample[int(self.counter)]
            self.counter += self.step
            if self.counter >= (self.chunklength-1):
                self.counter -= self.chunklength
            block.append(s)
        return block

    def gettestblock(self):
        #128 samples per cycle
        #@44100Hz freq= 344Hz
        block = []
        for j in range(0, 16):
            for i in range(-64, 64):
                #block.append(i*128)
                block.append(np.sin(np.pi*(i/64))*32000)
        assert len(block) == 2048
        return block

if __name__ == '__main__':
    app = AudioHandler()
    app.play()