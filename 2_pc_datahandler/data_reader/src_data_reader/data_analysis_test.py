import unittest
from data_reader.src_data_reader.data_analysis import analysis_frequency
from src import TransientData
import numpy as np

class DataAnalysisTest(unittest.TestCase):
    def setUp(self):
        self._sinuswave = self._generate_sinuswave()

    def _generate_sinuswave(self):
        fs = 1000
        duration = 1
        target_freq = 12

        num_samples = int(fs * duration)
        timestamps = np.linspace(0, duration, num_samples, endpoint=False)
        sinewave = np.sin(2 * np.pi * target_freq * timestamps)
        rawdata = np.zeros((num_samples, 1))
        rawdata[:, 0] = sinewave
        return TransientData(timestamps=timestamps, rawdata=rawdata, sampling_rate=fs, error_flags=None, channels=[1])
    

    def test_analysis_frequency(self):
        result =analysis_frequency(self._sinuswave, selected_channel=0)

        self.assertEqual(round(result[0]), 12)
        self.assertEqual(round(result[1]), self._sinuswave.sampling_rate)
