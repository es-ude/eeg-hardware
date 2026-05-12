import h5py
import time
from src import EEGDeviceMetadata, EEGDeviceConfig
from dataclasses import asdict
from .poti import PotiConfig

class H5Handler:
    _recording_name: str
    _metadata: EEGDeviceMetadata
    _eeg_device_config: EEGDeviceConfig
    _h5file: h5py.File
    _grp_ad7779: h5py.Group
    _length_ad7779: int

    def __init__(self, recording_name: str, metadata: EEGDeviceMetadata, eeg_device_config: EEGDeviceConfig, poti_values: PotiConfig) -> None:
        """Class to handle H5 file writing for EEG data, including initialization and appending data

        Args:
            recording_name (str): Filename for the H5 file
            metadata (EEGDeviceMetadata): Metadata information about the measurement
            eeg_device_config (EEGDeviceConfig): Configuration parameters for the EEG device
            poti_values (PotiConfig): Potentiometer configuration values for the instrumentation amplifier
        """  
        self._recording_name = recording_name
        self._metadata = metadata
        self._eeg_device_config = eeg_device_config
        self._poti_values = poti_values
        self._h5file, self._grp_ad7779 = self._init_h5_file_writer()
        self._length_ad7779 = 0
        self._num_of_data_in_buffer = 0


    @property
    def get_file_length(self) -> int:
        """Get the current length of the ad7779 dataset in the H5 file

        Returns:
            int: The length of the ad7779 dataset
        """        
        return self._length_ad7779


    def _init_h5_file_writer(self) -> tuple[h5py.File, h5py.Group]:
        """Initialize the H5 file and create necessary groups and datasets

        Returns:
            tuple[h5py.File, h5py.Group]: The H5 file object and the group for ad7779 data
        """
        file =h5py.File(f"{self._recording_name}_data.h5", "w")
        # Output Metadata as attributes
        file.attrs['created_at'] = time.ctime()
        file.attrs["version"] = "2.0"

        # generate group for ad7779
        grp_ad7779 = file.create_group("ad7779_data")
        
        #Write metadata attributes
        for key, value in asdict(self._metadata).items():
            grp_ad7779.attrs[key] = value
        for key, value in asdict(self._poti_values).items():
            grp_ad7779.attrs[key] = value
        grp_ad7779.attrs["measurement_duration"] = self._eeg_device_config.measure_duration
        grp_ad7779.attrs["adc_samplingrate"] = self._eeg_device_config.adc_samplingrate
        grp_ad7779.attrs["channel_mask"] = self._eeg_device_config.channel_mask
        grp_ad7779.attrs["adc_pga_gain"] = self._eeg_device_config.adc_pga_gain

        # Create datasets with maxshape for appending data
        grp_ad7779.create_dataset('timestamps', shape=(0,), maxshape=(None,), dtype='int64', chunks=True)
        grp_ad7779.create_dataset('measurements', shape=(0, 8), maxshape=(None, 8), dtype='int32', chunks=True)
        grp_ad7779.create_dataset('alerts', shape=(0, 8), maxshape=(None, 8), dtype='int8', chunks=True)
        return file, grp_ad7779


    def append_data_ad7779(self, timestamps: float, measurements: list, alerts: list) -> None:
        """Append data to the ad7779 datasets in the H5 file

        Args:
            timestamps (int): timestamp value to the datapoint
            measurements (list): list of measurement values for all channels at the data point
            alerts (list): a list of alert bits for all channels of the data point
        """
        dset_time =self._grp_ad7779["timestamps"]
        dset_meas =self._grp_ad7779["measurements"]
        dset_alert =self._grp_ad7779["alerts"]

        current_length = self._length_ad7779
        self._length_ad7779 += len(timestamps)

        dset_time.resize((self._length_ad7779,))
        dset_meas.resize((self._length_ad7779, 8))
        dset_alert.resize((self._length_ad7779, 8))
        
        dset_time[current_length:self._length_ad7779] = timestamps
        dset_meas[current_length:self._length_ad7779, :] = measurements
        dset_alert[current_length:self._length_ad7779] = alerts
        
        if self._num_of_data_in_buffer >= 10:
            self._h5file.flush()
            self._num_of_data_in_buffer = 0
        else:
            self._num_of_data_in_buffer += 1
            

    def close_h5_file(self) -> None:
        """Close the H5 file properly"""
        self._h5file.flush()
        self._h5file.close()