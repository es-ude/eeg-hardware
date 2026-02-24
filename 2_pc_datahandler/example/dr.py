from eeg_api import EEGDataReader
from pathlib import Path
import numpy as np


if __name__ == "__main__":
    path2file = Path("example")
    reader = EEGDataReader(path=path2file, load_case=0)
    data = reader.get_data()
    print(reader.get_metadata())

    #reader.post_process_rolling_median(window_size=5, threshold=10)
    reader.post_process_error_flags()
    data = reader.get_data()
    reader.plot_transient_data(data, channel_to_plot=0)
    reader.plot_histogram_timestamps(data)
    reader.frequency_analysis(data, 0)
    
    dt = np.diff(data.timestamps)
    print(np.median(dt), np.std(dt), np.min(dt), np.max(dt))
    print(np.unique(dt, return_counts=True))