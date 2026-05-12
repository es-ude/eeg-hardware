import numpy as np
from scipy.signal import find_peaks
from src import TransientData

def analysis_frequency(data: TransientData, selected_channel: int) -> None:
    """Analyze and print the dominant frequency in the selected channel data, with the corresponding sampling rate

    Args:
        selected_channel (int): Index of the channel to analyze
    """        
    num_samples = len(data.timestamps)
    fs = 1/np.median(np.diff(data.timestamps))

    fft_spectrum = np.fft.rfft(data.rawdata[:,selected_channel])
    fft_frequencies = np.fft.rfftfreq(num_samples, d=1 / fs)
    amplitudes = np.abs(fft_spectrum)

    peak_index = np.argmax(amplitudes[1:]) + 1
    detected_freq = fft_frequencies[peak_index]
    return (detected_freq, fs)
    #print(f"Dominante Frequenz: {detected_freq:.2f} Hz (@ {fs:.2f} Hz)")


def run_find_peaks(data: TransientData, selected_channel: int, min_distance: int = 5) -> np.ndarray:
    """Find peaks in the selected channel data, robust against outliers.

    Args:
        selected_channel (int): Index of the channel to analyze
        min_distance (int): Minimaler Abstand zwischen zwei Peaks in Samples.
    
    Returns:
        np.ndarray: Indices of the detected peaks
    """
    signal = data[:, selected_channel]
    min_height = np.mean(signal) + 0.5 * np.std(signal)
    min_prominence = 1.0 * np.std(signal) 
    
    peaks, _ = find_peaks(
        signal, 
        height=min_height, 
        prominence=min_prominence, 
        distance=min_distance
    )
    if len(peaks) == 0:
        return 0
    peak_y_values = signal[peaks]
    median_val = np.median(peak_y_values)
    return float(median_val)
    