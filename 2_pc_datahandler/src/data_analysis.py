import numpy as np
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