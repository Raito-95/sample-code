import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt

class AudioRecorder:
    def __init__(self, chunk_size=1024, sample_format=pyaudio.paInt16, channels=2, fs=44100):
        self.chunk_size = chunk_size
        self.sample_format = sample_format
        self.channels = channels
        self.fs = fs
        self.frames = []
        self.run = 0
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.sample_format, channels=self.channels, rate=self.fs, frames_per_buffer=self.chunk_size, input=True)
        self.fig, self.ax = plt.subplots()

    def record(self, num_frames=1000, output_file="recorded_audio.wav"):
        print("### Recording Started ###")
        while self.run < num_frames:
            data = self.stream.read(self.chunk_size)
            self.frames.append(data)
            self.run += 1
            print(f'Recording count: {self.run}')
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        print('### Recording Ended ###')
        wf = wave.open(output_file, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def visualize(self, input_file="recorded_audio.wav"):
        print('Creating Waveform Plot...')
        raw = wave.open(input_file)
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
