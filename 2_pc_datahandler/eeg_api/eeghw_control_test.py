import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from eeg_api.eeghw_control import ApiEEGDeviceController, characteristics_dataframes
import queue
import serial


class TestApiEEGDeviceController(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        self.controller = ApiEEGDeviceController.__new__(ApiEEGDeviceController)
        self.controller._byte_buffer = bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09,
                                0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x13,
                                0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D,
                                0x1E, 0x1F, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25])


    def test_read_serial_data(self):
        self.controller._deployed_serial_connection = MagicMock()
        self.controller._byte_buffer = bytearray()
        self.controller._packet_length = 38
        self.controller._data_queue = MagicMock()
        self.controller._running = True

        valid_packet = bytearray([0xAA] + [0x00]*36 + [0xBB])  # A valid packet with start and end bytes
        self.controller._check_packet_number = MagicMock(return_value=True)
        p_mock = PropertyMock(side_effect=[38, 0])
        type(self.controller._deployed_serial_connection).in_waiting = p_mock
        self.controller._deployed_serial_connection.read.return_value = valid_packet
        
        call_counter = {'count': 0}

        def in_waiting_logik():
            call_counter['count'] += 1
            
            if call_counter['count'] == 1:
                return 38
            else:
                self.controller._running = False 
                return 0


    def test_check_packet_number_is_not_set(self):
        """Check if the _check_packet_number method works correctly when no expected packet number is set"""
        self.controller._expected_packet_number = None
        packet_number = 4

        result =self.controller._check_packet_number(packet_index = packet_number)
        self.assertEqual(result, True) #Check the return value of the function
        self.assertEqual(self.controller._expected_packet_number, packet_number + 1) #Check if the expected packet number is set correctly


    def test_check_packet_number_is_set_and_correct(self):
        """Check if the _check_packet_number method works correctly when the expected packet number is set and matches the packet number in the buffer"""
        self.controller._expected_packet_number = 2
        packet_number = 2
        
        result =self.controller._check_packet_number(packet_index = packet_number)
        self.assertEqual(result, True) #Check the return value of the function
        self.assertEqual(self.controller._expected_packet_number, packet_number + 1) #Check if the expected packet number is updated correctly


    def test_check_packet_number_is_set_and_incorrect(self):
        """Check if the _check_packet_number method works correctly when the expected packet number is set and does not match the packet number in the buffer"""
        self.controller._expected_packet_number = 1
        packet_number = 3
        
        result =self.controller._check_packet_number(packet_index = packet_number)
        self.assertEqual(result, False) #Check the return value of the function
        self.assertEqual(self.controller._expected_packet_number, packet_number+1) #Check if the expected packet number remains unchanged


    def test_check_packet_number_wrap_around(self):
        """Check if the _check_packet_number method works correctly when the packet number wraps around from 255 to 0"""
        self.controller._expected_packet_number = 0xFF
        packet_number = 0xFF
        
        result =self.controller._check_packet_number(packet_index = packet_number)
        self.assertEqual(result, True) #Check the return value of the function
        self.assertEqual((self.controller._expected_packet_number), 0) #Check if the expected packet number is updated correctly


    @patch ("eeg_api.eeghw_control.H5Handler")    
    def test_init_h5_file_writer(self, mock_h5handler):
        self.controller._recording_name = "test_recording"
        self.controller._metadata = MagicMock()
        self.controller._eeg_device_config = MagicMock()

        self.controller._init_h5_file_writer()
        mock_h5handler.assert_called_once_with(recording_name="test_recording", metadata=self.controller._metadata, eeg_device_config=self.controller._eeg_device_config)

        

if __name__ == '__main__':
    unittest.main()