import numpy as np
import wave
from scipy.io import wavfile
from scipy.signal import butter, filtfilt
import time
import pyaudio
import threading

BUFFER_SIZE = 1024
MIN_CUTOFF_HIGH = 1000
MAX_CUTOFF_HIGH = 22000
MIN_BAND = 500
MAX_BAND = 1000
MID_BAND = MIN_BAND + MAX_BAND / 2
MIN_CUTOFF_LOW = 15
MAX_CUTOFF_LOW = 500
INT16_MAX_VALUE = 32767
FRAME_CHUNK = 20

class Filter (threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.is_thread_initiated = False
        self.is_thread_alive = True
        self.daemon = True
        self.output_sum = None
        self.counter = 0
        self.low_bound = 0
        self.frame_count = 1024
        self.low_coefficient = 0.5
        self.band_coefficient = 0.5
        self.high_coefficient = 0.5
        self.stream = None
        self.low_signal = 0
        self.band_signal = 0
        self.high_signal = 0

    def read_file_data(self, file_name):
        self.file_name = file_name
        self.sr, self.signal = wavfile.read(self.file_name)
        self.spec_indicator = wave.open(self.file_name, 'rb')

    def is_stream_paused(self):
        return self.stream and self.stream.is_stopped()

    def pause_stream(self):
        self.stream.stop_stream()

    def play_stream(self):
        self.stream.start_stream()

    def set_low_coefficient(self, value):
        self.low_coefficient = float(value)

    def set_band_coefficient(self, value):
        self.band_coefficient = float(value)

    def set_high_coefficient(self, value):
        self.high_coefficient = float(value)

    def butter_lowpass(self, cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def butter_lowpass_filter(self, data, cutoff, fs, order=5):
        b, a = self.butter_lowpass(cutoff, fs, order=order)
        y = filtfilt(b, a, data, axis=0)
        return y

    def butter_bandpass(self, lowcut, highcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a

    def butter_bandpass_filter(self, data, lowcut, highcut, fs, order=5):
        b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
        y = filtfilt(b, a, data, axis=0)
        return y

    def butter_highpass(self, cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        return b, a

    def butter_highpass_filter(self, data, cutoff, fs, order=5):
        b, a = self.butter_highpass(cutoff, fs, order=order)
        y = filtfilt(b, a, data, axis=0)
        return y

    def get_highest_value(self, data):
        highest = 0

        for sub_arrays in data:
            for values in sub_arrays:
                if values > highest:
                    highest = values

        return highest

    def get_down_sampling_factor(self, high_value, level=0):
        factor = 1
        if high_value >= INT16_MAX_VALUE:
            factor = self.get_down_sampling_factor(high_value / 2, level + 1)
            factor = factor*2
        return factor

    def callback(self, in_data, frame_count, time_info, status):
        self.counter += 1
        self.frame_count = frame_count
        self.low_bound = (self.counter - 1) * frame_count
        high_bound = self.counter * frame_count
        return self.output_sum[self.low_bound:high_bound].tobytes(), pyaudio.paContinue

    def before_run(self):
        self.is_thread_initiated = True
        fs = self.sr
        cutoff_low = MAX_CUTOFF_LOW
        order_low = 2

        highest_value = self.get_highest_value(self.signal)
        down_sampling_factor = self.get_down_sampling_factor(highest_value)

        output_low = self.butter_lowpass_filter(self.signal, cutoff_low, fs, order_low)
        self.low_signal = np.int16(output_low / down_sampling_factor)
        del output_low

        cutoff_high = MIN_CUTOFF_HIGH
        order_high = 2

        output_high = self.butter_highpass_filter(self.signal, cutoff_high, fs, order_high)
        self.high_signal = np.int16(output_high / down_sampling_factor)
        del output_high

        low_band = MIN_BAND
        high_band = MAX_BAND
        order_band = 2

        output_band = self.butter_bandpass_filter(self.signal, low_band, high_band, fs, order_band)
        self.band_signal = np.int16(output_band / down_sampling_factor)
        del output_band

        self.output_sum = np.empty((len(self.low_signal), 2))

        p = pyaudio.PyAudio()
        self.stream = p.open(format=p.get_format_from_width(self.spec_indicator.getsampwidth()),
                        channels=self.spec_indicator.getnchannels(),
                        rate=fs,
                        output=True,
                        stream_callback=self.callback)

        self.stream.start_stream()

    def play(self):
        while self.stream.is_active():
            self.output_sum = np.int16(self.low_coefficient * self.low_signal) \
                        + np.int16(self.band_coefficient * self.band_signal) \
                        + np.int16(self.high_coefficient * self.high_signal)

            time.sleep(0.05)

        if(not self.is_stream_paused()):
            self.stream.stop_stream()
            self.stream.close()
            self.spec_indicator.close()
            p.terminate()
            self.is_thread_alive = False

    def run(self):
        self.before_run()
        while self.is_thread_alive:
            if not self.is_stream_paused():
                self.play()
            time.sleep(1)