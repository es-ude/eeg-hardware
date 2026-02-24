from src import TransientMetadata
from pathlib import Path
import numpy as np
import h5py

def load_files(master_path: Path, load_case: int) -> Path:
    """Get file paths from the specified directory

    Args:
        master_path (Path): Path to the directory containing the h5 files
        load_case (int, optional): Index of the file to load

    Raises:
        FileExistsError: If no files are found in the specified directory
    
    Returns:
        Path: Path to the selected h5 file
    """
    find_files = master_path.glob("*.h5")
    chck = [file.stem for file in list(find_files)]
    if not len(chck):
        raise FileExistsError("No files found in the specified directory.")
    find_data = list(master_path.glob("*_data.h5"))
    find_data.sort()
    data_path = find_data[load_case]
    
    print(f"Loading data file: {data_path}")
    return data_path


def read_h5_file(path_to_file: Path) -> np.ndarray:    
    """Read h5 file and output timestamps, measurements and error flags

    Args:
        path_to_file (Path): Path to the h5 file
    
    Returns:
        np.ndarray: alerts, measurements, timestamps
        TransientMetadata: metadata of the measurement
    """
    try:
        raw_extraction = h5py.File(path_to_file, 'r')
    except FileNotFoundError as e:
        print(f"Error reading files: {e}")
    alerts =np.array(raw_extraction["ad7779_data"]["alerts"])
    measurements =np.array(raw_extraction["ad7779_data"]["measurements"])
    timestamps =np.array(raw_extraction["ad7779_data"]["timestamps"])
    metadata = TransientMetadata(measurement_duration = raw_extraction["ad7779_data"].attrs.get("measurement_duration"),
                                    adc_samplingrate = raw_extraction["ad7779_data"].attrs.get("adc_samplingrate"),
                                    channel_mask = raw_extraction["ad7779_data"].attrs.get("channel_mask"),
                                    waveform_generator = raw_extraction["ad7779_data"].attrs.get("waveform_generator"),
                                    waveform_generator_frequency = raw_extraction["ad7779_data"].attrs.get("waveform_generator_frequency"),
                                    waveform_generator_amplitude = raw_extraction["ad7779_data"].attrs.get("waveform_generator_amplitude"),
                                    waveform_type = raw_extraction["ad7779_data"].attrs.get("waveform_type"))
    if float(raw_extraction.attrs.get("version", 0)) == 2.0:
        pass
        return alerts, measurements, timestamps, metadata
    else:
        return alerts, measurements, timestamps, metadata