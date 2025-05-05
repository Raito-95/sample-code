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
        self.audio = pyaudio.PyAudio()

        try:
            self.stream = self.audio.open(
                format=self.sample_format,
                channels=self.channels,
                rate=self.fs,
                frames_per_buffer=self.chunk_size,
                input=True,
            )
        except Exception as e:
            print(f"[Error] Failed to open audio stream: {e}")
            self.audio.terminate()
            raise

        self.fig, self.ax = plt.subplots()

    def record(self, output_file="recorded_audio.wav"):
        print("### Recording Started (Press Ctrl+C to stop) ###")
        try:
            while True:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.frames.append(data)
                print(f"Recorded chunks: {len(self.frames)}", end="\r")
        except KeyboardInterrupt:
            print("\n### Recording Stopped by User ###")
        except Exception as e:
            print(f"[Error] During recording: {e}")
        finally:
            self._save_wave(output_file)
            self.cleanup()

    def _save_wave(self, output_file):
        try:
            wf = wave.open(output_file, "wb")
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.sample_format))
            wf.setframerate(self.fs)
            wf.writeframes(b"".join(self.frames))
            wf.close()
            print(f"[Saved] Audio saved to '{output_file}'")
        except Exception as e:
            print(f"[Error] Saving audio file failed: {e}")

    def cleanup(self):
        if self.stream.is_active():
            self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def visualize(self, input_file="recorded_audio.wav"):
        print("Creating Waveform Plot...")
        try:
            raw = wave.open(input_file, "rb")
            signal = raw.readframes(-1)
            signal = np.frombuffer(signal, dtype="int16")
            f_rate = raw.getframerate()
            raw.close()

            # Handle stereo by selecting one channel
            if self.channels == 2:
                signal = signal[::2]

            time = np.linspace(0, len(signal) / f_rate, num=len(signal))
            self.ax.plot(time, signal)
            plt.title("Sound Waveform")
            plt.xlabel("Time (seconds)")
            plt.ylabel("Amplitude")
            plt.grid(True)
            plt.show()
        except FileNotFoundError:
            print(f"[Error] File '{input_file}' not found.")
        except Exception as e:
            print(f"[Error] During visualization: {e}")


if __name__ == "__main__":
    audio_recorder = AudioRecorder()
    audio_recorder.record()
    audio_recorder.visualize()
