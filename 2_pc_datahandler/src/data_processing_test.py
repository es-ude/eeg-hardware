import unittest
import numpy as np
from src import extract_channel_data, extract_error_flags

class DataProcessingTest(unittest.TestCase):
    def setUp(self):
        self._raw_data_packet = np.array([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09,
                                           0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x13,
                                           0x14, 0x15, 0x16, 0x17], dtype=np.uint8)


    def test_extract_channel_data(self):
        #First channel: max positive value
        self._raw_data_packet[0] = 0x7F
        self._raw_data_packet[1] = 0xFF
        self._raw_data_packet[2] = 0xFF
        #Last channel: negative value
        self._raw_data_packet[-3] = 0xFF
        self._raw_data_packet[-2] = 0xFF
        self._raw_data_packet[-1] = 0xFF

        result = extract_channel_data(self._raw_data_packet)
        self.assertEqual(len(result), 8)
        self.assertEqual(result[0], 8388607)
        self.assertEqual(result[7], -1)


    def test_extract_error_flags(self):
        # Set error flags byte to 0b10101010
        flag_byte = 0b10101010

        result = extract_error_flags(error_flag_byte=flag_byte)
        expected_flags = [0, 1, 0, 1, 0, 1, 0, 1]
        self.assertEqual(result, expected_flags)