import unittest
import numpy as np
from data_reader.src_data_reader.data_post_processing import post_process_rolling_median, post_process_error_flags, elapsed_time_convert_to_seconds

class DataPostProcessingTest(unittest.TestCase):
    def setUp(self):
        self._measurements = np.array([[11,21,31,41,51,61,71,81], [12,22,32,47,52,62,72,82], [13,23,33,43,53,63,73,83], [14,24,34,44,54,64,74,84]], dtype=int) # 4 data points, 8 channels
        self._error_flags = np.array([[0,0,0,0,0,0,0,0], [0,0,0,1,0,0,0,0], [0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0]], dtype=int) 


    def test_post_process_rolling_median_single_outlier_removal(self):
        self._measurements = np.array([[10], [10], [10], [10], [100], [10], [10], [10], [10], [10]], dtype=int)

        result = post_process_rolling_median(self._measurements.copy(), window_size=5, threshold=25)
        self.assertEqual(result[4, 0], 10.0)
        self.assertEqual(result[0, 0], 10.0)

    def test_post_process_rolling_median_test_no_change_below_threshold(self):
        self._measurements = np.array([[10], [10], [30], [10], [10]], dtype=int)

        result = post_process_rolling_median(self._measurements.copy(), window_size=3, threshold=25)
        self.assertEqual(result[2, 0], 30.0)
    
    def test_post_process_rolling_median_channel_independence(self):
        self._measurements = np.array([[10,5], [10,5], [100,5], [10,5], [10,5]], dtype=float)
        
        result = post_process_rolling_median(self._measurements.copy(), window_size=3, threshold=25)
        self.assertEqual(result[2, 0], 10.0)  # First channel corrected
        self.assertEqual(result[2, 1], 5.0)  # Second channel unchanged


    def test_post_process_error_flags(self): #Test written
        result = post_process_error_flags(self._measurements, self._error_flags)
        self.assertEqual (result[:,3].tolist(), [41, 42, 43, 44]) # Check if data points are corerected

    def test_process_error_flags_at_start_end(self):
        self._measurements = np.array([[13,21,31,41,51,61,71,81], [12,22,32,42,52,62,72,82], [13,23,33,43,53,63,73,83], [14,24,34,44,54,64,74,84]], dtype=int) # 4 data points, 8 channels
        self._error_flags = np.array([[1,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,1], [0,0,0,0,0,0,0,0]], dtype=int) 
        
        result = post_process_error_flags(self._measurements, self._error_flags)
        assert result[:,0].tolist() == [13, 12, 13, 14] # Check if data points are unchanged
        assert result[:,7].tolist() == [81, 82, 83, 84] # Check if data points are unchanged
    
    def test_elapsed_time_convert_to_seconds(self):
        timestamps = np.array([1e6, 5e6, 10e6, 15e6, 20e6])  # in milliseconds
        expected = np.array([0.0, 4, 9, 14, 19])
        scale_time =   1e6# Convert milliseconds to seconds

        result = elapsed_time_convert_to_seconds(timestamps, scale_time)
        np.testing.assert_array_almost_equal(result, expected)