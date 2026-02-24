import unittest
from unittest.mock import patch
from pathlib import Path
from data_reader.src_data_reader.data_loading import load_files, read_h5_file

class DataLoadingTest(unittest.TestCase):
    def setUp(self):
        pass

    @patch('data_reader.src_data_reader.data_loading.Path.glob')
    def test_load_files_successfull(self, mock_glob):
        mock_glob.return_value = [Path("file1_data.h5"), Path("file2_data.h5")]
        master_path = Path("/mock/path")
        
        selected_file = load_files(master_path, 1)
        self.assertEqual(selected_file, Path("file2_data.h5"))
    
    @patch('data_reader.src_data_reader.data_loading.Path.glob')
    def test_load_files_no_files_found(self, mock_glob):
        mock_glob.return_value = []
        master_path = Path("/mock/path")
        
        with self.assertRaises(FileExistsError):
            load_files(master_path, 0)


    def test_read_h5_file_successful(self):
        result = read_h5_file(Path("data_reader/src_data_reader/test_data/uinttest_testdata.h5"))
        self.assertEqual(result[0][:,0].tolist(), [0,1,2,3,4,5,6,7,8,9]) # alerts first channel
        self.assertEqual(result[0][1].tolist(), [1,1,1,1,1,1,1,1]) # alerts second measurement
        self.assertEqual(result[1][:,0].tolist(), [0,1,2,3,4,5,6,7,8,9]) # measurements first channel
        self.assertEqual(result[1][1].tolist(), [1,1,1,1,1,1,1,1]) # measurements second read
        self.assertEqual(result[2].tolist(), [0,1,2,3,4,5,6,7,8,9]) # timestamps
        self.assertEqual(result[3].measurement_duration, 10) # metadata check
        self.assertEqual(result[3].channel_mask.tolist(), [0,1,0,1,0,1,0,1]) # metadata check
        self.assertEqual(result[3].waveform_generator, "Test_generator") # metadata check
        self.assertEqual(result[3].waveform_generator_frequency, 15) # metadata check
        self.assertEqual(result[3].waveform_generator_amplitude, 1) # metadata
        self.assertEqual(result[3].waveform_type, "sine") # metadata check