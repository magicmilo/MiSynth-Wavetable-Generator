# MiSynth-Wavetable-Generator Python3
Process, listen to and export wavetables for the MiSynth Project.
Run from main.py.
Input files are mono .wav uncompressed as high a sample rate as possible.

The final wavetable synthesizer uses 2048 sample length.
At middle-c (440Hz) gives an effective sample rate of 901,120Hz.
The application tries to mitigate this with dithering.

To maintain the same frequency with a 44.1KHz sample rate wav file.
Only 128 samples are used in playback 2^7 out of 2^11.
