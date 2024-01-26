import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt

chunk = 1024
sample_format = pyaudio.paInt16  # Sound format: paFloat32, paInt32, paInt24, paInt16, paInt8, paUInt8, paCustomFormat
channels = 2
fs = 44100                       # Audio sampling rate: 192000, 96000, 48000, 44100, 32000, 22050, 8000
filename = "audio.wav"

class AudioRecorder:
    def __init__(self):
        self.frames = []
        self.run = 0
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)
        self.fig, self.ax = plt.subplots()

    def record(self):
        print("### Recording Started ###")
        while self.run < 500:
            data = self.stream.read(chunk)
            self.frames.append(data)
            self.run += 1
            print(f'Recording count: {self.run}')
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        print('### Recording Ended ###')
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(self.audio.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def visualize(self):
        print('Creating Waveform Plot...')
        raw = wave.open(filename)
        signal = raw.readframes(-1)
        signal = np.frombuffer(signal, dtype="int16")
        f_rate = raw.getframerate()
        time = np.linspace(0, len(signal) / f_rate, num=len(signal))
        self.ax.plot(time, signal)
        plt.title("Sound Waveform")
        plt.xlabel("Time")
        plt.show()

if __name__ == '__main__':
    audio_recorder = AudioRecorder()
    audio_recorder.record()
    audio_recorder.visualize()
