import unittest
from unittest.mock import patch, MagicMock
from pylsl import cf_int64
from eeg_api.src_eeg_api.lsl_handler import LSLHandler

class TestLSLHandler(unittest.TestCase):
    def setUp(self):
        self._handler = LSLHandler.__new__(LSLHandler)

    @patch ('eeg_api.src_eeg_api.lsl_handler.StreamInfo')
    @patch ('eeg_api.src_eeg_api.lsl_handler.StreamOutlet')
    def test_create_lsl_outlet_daq(self, mock_stream_outlet, mock_stream_info):
        self._handler._name = "TestStream"
        self._handler._sampling_rate = 250
        mock_stream_info_instance = MagicMock()
        mock_stream_info.return_value = mock_stream_info_instance
        mock_stream_outlet_instance = MagicMock()
        mock_stream_outlet.return_value = mock_stream_outlet_instance

        outlet = self._handler.create_lsl_outlet_daq
        mock_stream_info.assert_called_once_with(
            name="TestStream",
            type='custom_daq',
            channel_count=17,
            nominal_srate=250,
            channel_format=cf_int64,
            source_id="TestStream_uid"
        )