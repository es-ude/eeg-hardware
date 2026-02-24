import unittest
from src import TransientMetadata
from unittest.mock import patch, MagicMock
from src import H5Handler, EEGDeviceConfig, PotiConfig


class H5HandlerTest(unittest.TestCase):
    def setUp(self):
        self.handler = H5Handler.__new__(H5Handler)  # Create an instance without calling __init__
        self.handler._num_of_data_in_buffer = 0
        self.handler._recording_name = "test_recording"
        self.handler._metadata = TransientMetadata(
            measurement_duration=671,
            adc_samplingrate=672,
            channel_mask=[1,1,1,1,1,1,1,1],
            waveform_generator="g_test",
            waveform_generator_frequency=673,
            waveform_generator_amplitude=674,
            waveform_type="t_test"
        )
        self.handler._eeg_device_config = EEGDeviceConfig(
            com_name="COM_TEST",
            measure_duration=671,
            adc_pga_gain=1,
            channel_mask=[1,1,1,1,1,1,1,1],
            sdo_driver_strength=3,
            adc_samplingrate=672,
            test_mode_enabled=False,
            adc_power_mode_high=True,
            error_header=False,
            reference_active_shielding=False,
            gain_instrument_amplifier=1
        )
        self.handler._poti_values = PotiConfig(gain=2, 
                                               calculated_resistor_value=1000, 
                                               poti_value=128, 
                                               actual_resistor_value=1000, 
                                               actual_gain_value=2) 


    @patch ("h5py.File")
    def test_init_h5_file_writer(self, mock_h5file):
        mock_file = MagicMock()
        mock_h5file.return_value = mock_file
        mock_group = MagicMock()
        mock_file.create_group.return_value = mock_group
        
        self.handler._init_h5_file_writer()
        mock_h5file.assert_called_with("test_recording_data.h5", "w")
        mock_group.attrs.__setitem__.assert_any_call("measurement_duration", 671)
        mock_group.attrs.__setitem__.assert_any_call("adc_samplingrate", 672)
        mock_group.attrs.__setitem__.assert_any_call("channel_mask", [1,1,1,1,1,1,1,1])
        mock_group.create_dataset.assert_any_call('timestamps', shape=(0,), maxshape=(None,), dtype='int64', chunks=True)
        mock_group.create_dataset.assert_any_call('measurements', shape=(0, 8), maxshape=(None, 8), dtype='int32', chunks=True)
        mock_group.create_dataset.assert_any_call('alerts', shape=(0, 8), maxshape=(None, 8), dtype='int8', chunks=True)
        mock_group.attrs.__setitem__.assert_any_call("gain", 2)
        mock_group.attrs.__setitem__.assert_any_call("calculated_resistor_value", 1000)
        mock_group.attrs.__setitem__.assert_any_call("poti_value", 128)
        mock_group.attrs.__setitem__.assert_any_call("actual_resistor_value", 1000)
        mock_group.attrs.__setitem__.assert_any_call("actual_gain_value", 2)

    

    def test_append_data_ad7779(self):
        self.handler._h5file = MagicMock()
        self.handler._grp_ad7779 = {
            "timestamps": MagicMock(),
            "measurements": MagicMock(),
            "alerts": MagicMock()
        }
        self.handler._length_ad7779 = 0
        
        timestamps = [1001, 1002]
        measurements = [[10,20,30,40,50,60,70,80], [11,21,31,41,51,61,71,81]]
        alerts = [[0,0,0,0,0,0,0,0], [1,1,1,1,1,1,1,1]]
        
        self.handler.append_data_ad7779(timestamps, measurements, alerts)

        self.handler._grp_ad7779["timestamps"].resize.assert_called_with((2,))
        self.handler._grp_ad7779["measurements"].resize.assert_called_with((2, 8))
        self.handler._grp_ad7779["alerts"].resize.assert_called_with((2, 8))
