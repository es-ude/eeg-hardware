import unittest
from unittest.mock import patch, MagicMock
import serial
from eeg_api.src_eeg_api.serial_handler import SerialHandler

class TestSerialHandler(unittest.TestCase):
    def setUp(self):
        self._handler = SerialHandler.__new__(SerialHandler)

    @patch ('eeg_api.src_eeg_api.serial_handler.serial.Serial')
    def test_get_serial_connection(self, mock_serial):
        mock_serial_instance = MagicMock()
        mock_serial.return_value = mock_serial_instance
        self._handler._serial_connection = mock_serial_instance

        result  = self._handler.get_serial_connection
        self.assertEqual(result, mock_serial_instance)
    

    @patch ("eeg_api.src_eeg_api.serial_handler.list_ports.comports")
    def test_read_usb_properties(self, mock_comports):
        """Test the __read_usb_properties methode from the SerialHandler class, this method scans the available COM ports and retrieves their USB properties."""    
        mock_port1 = MagicMock()
        mock_port1.device = "/dev/ttyUSB0"
        mock_port1.pid = 0x1234
        mock_port1.vid = 0x5678

        mock_port2 = MagicMock()
        mock_port2.device = "/dev/ttyUSB1"
        mock_port2.pid = 0x8765
        mock_port2.vid = 0x4321
        mock_comports.return_value = [mock_port1, mock_port2]
    
        return_value_usb_properties = self._handler._SerialHandler__read_usb_properties

        self.assertEqual([{"com" : mock_port1.device, 
                           "pid" : mock_port1.pid, 
                           "vid" : mock_port1.vid},
                           {"com" : mock_port2.device, 
                           "pid" : mock_port2.pid, 
                           "vid" : mock_port2.vid}]
                           , return_value_usb_properties)
    

    @patch ("eeg_api.src_eeg_api.serial_handler.list_ports.comports")
    def test_scan_com_name(self, mock_comports):
        mock_port1 = MagicMock()
        mock_port1.device = "/dev/ttyUSB0"
        mock_port1.pid = 0x1234
        mock_port1.vid = 0x5678

        mock_port2 = MagicMock()
        mock_port2.device = "/dev/ttyUSB1"
        mock_port2.pid = 0x0009
        mock_port2.vid = 0x2E8A
        mock_comports.return_value = [mock_port1, mock_port2]
    
        return_value = self._handler._scan_com_name        
        self.assertEqual([mock_port2.device], return_value)


    @patch("eeg_api.src_eeg_api.serial_handler.serial.Serial")
    @patch("eeg_api.src_eeg_api.serial_handler.time.sleep")
    def test_init_serial_connection(self, mock_sleep, mock_serial_cls):
        self._handler._com_name = "/dev/ttyUSB0"
        self._handler._baudrate = 115200
        self._handler._time_out = 1

        expected_serial_instance = MagicMock()
        mock_serial_cls.return_value = expected_serial_instance
        
        self._handler._init_serial_connection()
        mock_serial_cls.assert_called_once_with(port=self._handler._com_name,
                                                baudrate=self._handler._baudrate,
                                                inter_byte_timeout=1,
                                                bytesize=serial.EIGHTBITS, 
                                                parity=serial.PARITY_NONE, 
                                                stopbits=serial.STOPBITS_ONE, 
                                                xonxoff=False,
                                                rtscts=False,
                                                dsrdtr=False,
                                                timeout=self._handler._time_out)
    
    #Needs to be implemented
    def test_clear_serial_buffer(self):
        pass