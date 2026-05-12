import numpy as np
import pandas

def post_process_rolling_median(measurements: np.ndarray, window_size: int=5, threshold: int=25) -> np.ndarray:
    """Post-process the data to remove outliers using rolling median

    Args:
        measurements (np.ndarray): Numpy array of measurements, shape (num_data_points, num_channels)
        window_size (int, optional): Window size for rolling median calculation. Defaults to 5.
        threshold (int, optional): Threshold for detecting outliers. Defaults to 25.

    Returns:
        np.ndarray: Numpy array of measurements with outliers replaced by rolling median values
    """
    for channel_index in range(measurements.shape[1]):
        data_channel = measurements[:, channel_index]
        data_series = pandas.Series(data_channel)
        rolling_median = data_series.rolling(window=window_size, center=True).median()
        deviation = np.abs(data_series - rolling_median)
        error_mask = (deviation > threshold).fillna(False)
    
        clean_data = data_series.copy()
        clean_data[error_mask] = rolling_median[error_mask]

        rolling_median_2 = clean_data.rolling(window=window_size, center=True).median()
        deviation_2 = np.abs(clean_data - rolling_median_2)
        outlier_mask_2 = (deviation_2 > threshold).fillna(False)
    
        clean_data[outlier_mask_2] = rolling_median_2[outlier_mask_2]
        measurements[:, channel_index] = clean_data.values
    return measurements


def post_process_error_flags(measurements: np.ndarray, error_flags: np.ndarray) -> np.ndarray:
    """Post-process error flags to interpolate erroneous data points

    Args:
        measurements (np.ndarray): Numpy array of measurements, shape (num_data_points, num_channels)
        error_flags (np.ndarray): Numpy array of error flags, shape (num_data_points, num_channels)

    Returns:
        np.ndarray: Numpy array of measurements with interpolated values for erroneous data points
    """     
    for channel in range(error_flags.shape[1]):
        for index, error_flag_channel in enumerate(error_flags[:, channel]):
            if error_flag_channel == 0: # No Error detected
                continue
            
            if index ==0 or index == len(error_flags[:, channel]) -1:
                print("ERROR FLAG AT START OR END OF RECORDING, SKIPPING INTERPOLATION")
                continue # Skip first and last error flag, as no interpolation is possible

            total_error_values_in_sequence =0
            while True:
                if index + total_error_values_in_sequence +1 >= len(error_flags[:, channel]): # Prevent index out of range
                    break
                if error_flags[:, channel][index + total_error_values_in_sequence +1] ==1:
                    total_error_values_in_sequence +=1
                else:
                    break
            total_error_values_in_sequence += 1# Include the first error, one error is every time in sequence
            lower_bound = measurements[:, channel][index-1]
            upper_bound = measurements[:, channel][index + total_error_values_in_sequence]
            correction_values = np.linspace(lower_bound, upper_bound, total_error_values_in_sequence +2)
            for i in range(total_error_values_in_sequence):
                measurements[:, channel][index + i] = correction_values[i +1]
    return measurements


def elapsed_time_convert_to_seconds(timestamps: np.ndarray, scale_time: float) -> np.ndarray:
    """"Converts absolute timestamps in microseconds to elapsed time in seconds

    Args:
        timestamps (np.ndarray): Numpy array of absolute timestamps
        scale_time (float): Scaling factor to convert timestamps to seconds

    Returns:
        np.ndarray: Converted timestamps in seconds
    """      
    timestamps_float = timestamps.astype(np.float64)
    first_timestamp =timestamps[0]

    converted_timestamps = (timestamps_float - first_timestamp) / scale_time
    return converted_timestamps