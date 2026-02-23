import numpy as np
from pathlib import Path
from src import TransientData, TransientMetadata
from .src_data_reader import post_process_rolling_median, post_process_error_flags, elapsed_time_convert_to_seconds
from .src_data_reader import plot_transient_data, plot_histogram_timestamps
from .src_data_reader import analysis_frequency
from .src_data_reader import load_files, read_h5_file


class EEGDataReader:
    _scale_data: float = 5. / 2 ** 24
    _scale_time: float = 1e6 # microseconds to seconds
    
    _error_flags: np.ndarray # alert data
    _measurements: np.ndarray # measurements data
    _timestamps: np.ndarray # timestamps in microseconds
    _metadata : TransientMetadata # metadata from h5 file, for the loaded recording
    _packet_numbers: list # packet numbers from each data packet

    _path_to_selected_file: Path #Path to the binary data file (including Datapoints and Timestamps, Error Flags, active channels)


    def __init__(self, path: str | Path, load_case: int=0) -> None:
        """Initialize EEGDataReader with file paths
        :param path:        Path to the directory containing binary files
        :param load_case:   Integer with number of processing file
        :return:            None
        """
        
        self._path_to_selected_file = self._load_files(Path(path), load_case)
        self._error_flags, self._measurements, self._timestamps, self._metadata = self._read_h5_file()

        self._timestamps = self._elapsed_time_convert_to_seconds()


    # ========== API METHODS ==========
    def get_data(self) -> TransientData:
        """Get the processed data as TransientData object

        Raises:
            ValueError: File is not, the list of data points or timestamps is None

        Returns:
            TransientData: Processed data as TransientData object
        """       
        if self._measurements is None or self._timestamps is None or self._error_flags is None:
            raise ValueError("File not loaded. Please load file before getting data!")

        fs = 1/np.median(np.diff(self._timestamps))
        return TransientData(
            rawdata= self._scale_data * self._measurements,
            timestamps=self._timestamps,
            sampling_rate=float(fs),
            error_flags=self._error_flags,
            channels= self._metadata.channel_mask
        )


    def get_metadata(self) -> TransientMetadata:
        """Hands back metadata from the loaded recording

        Returns:
            TransientMetadata: Metadata for the loaded recording
        """        
        return self._metadata
    

    def get_path2file(self) -> Path:
        """Get the path to the data file

        Returns:
            Path: Path to the data file
        """        
        return self._path_to_selected_file
    

    @staticmethod
    def plot_transient_data(data: TransientData, channel_to_plot: int) -> None:
        """Plot the measured data for a selected channel

        Args:
            data (TransientData): Object containing the measured transient data and timestamps
            channel_to_plot (int): Index of the channel to plot (0-based)
        """        
        plot_transient_data(data, channel_to_plot)


    @staticmethod
    def plot_histogram_timestamps(data: TransientData) -> None:
        """Plot histogram for timestamps differences

        Args:
            data (TransientData): Object containing the measured transient data and timestamps
        """        
        plot_histogram_timestamps(data)


    @staticmethod
    def frequency_analysis(data: TransientData, selected_channel: int) -> None:
        """Analyze and print the dominant frequency in the selected channel data, with the corresponding sampling rate

        Args:
            data (TransientData): Object containing the measured transient data and timestamps
            selected_channel (int): Index of the channel to analyze
        """        
        result = analysis_frequency(data, selected_channel)
        print(f"Dominant frequency: {(result[0])}Hz at Sampling Rate: {(result[1])}Hz")


    def post_process_rolling_median(self, window_size: int, threshold: int) -> None:
        """Post-process the data to remove outliers using rolling median

        Args:
            window_size (int): window size for rolling median calculation
            threshold (int): threshold for detecting outliers
        """        
        post_process_rolling_median(self._measurements, window_size, threshold)


    def post_process_error_flags(self) -> None:
        """Post-process error flags to interpolate erroneous data points"""        
        post_process_error_flags(self._measurements, self._error_flags)


    # ========== INTERNAL METHODS ==========
    def _load_files(self, master_path: Path, load_case: int=0) -> Path:
        """Load file paths from the specified directory

        Args:
            master_path (Path): Path to the directory containing the h5 files
            load_case (int, optional): Index of the file to load. Defaults to 0.

        Returns:
            Path: Path to the selected h5 file
        """        
        return load_files(master_path, load_case)

    
    def _read_h5_file(self) -> np.ndarray:
        """Read h5 file and output timestamps, measurements and error flags

        Returns:
            np.ndarray: alerts, measurements, timestamps
            TransientMetadata: metadata of the measurement
        """        
        return read_h5_file(self._path_to_selected_file)
        

    def _elapsed_time_convert_to_seconds(self) -> np.ndarray:
        """Convert elapsed time from microseconds to seconds

        Returns:
            np.ndarray: Numpy array of timestamps in seconds
        """        
        return elapsed_time_convert_to_seconds(self._timestamps, scale_time=self._scale_time)