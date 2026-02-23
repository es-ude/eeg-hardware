import matplotlib.pyplot as plt
import numpy as np
from src import TransientData


def plot_transient_data(data: TransientData, channel_to_plot) -> None:
    """Plot the data points"""
    if channel_to_plot < 0 or channel_to_plot >= data.rawdata.shape[1]:
        raise ValueError("Invalid channel index to plot.")
    
    plt.plot(data.timestamps, data.rawdata[:, channel_to_plot], color='k', marker='.', markersize=4)
    plt.xlim([data.timestamps[0], data.timestamps[-1]])
    plt.xlabel("Timestamp")
    plt.ylabel(f"ADC output V]")
    plt.tight_layout()
    plt.show()


def plot_histogram_timestamps(data: TransientData) -> None:
    """Plot histogram for timestamps differences"""
    dt = np.diff(data.timestamps)

    plt.figure(figsize=(10, 6))
    plt.hist(dt, bins=2000, color='blue', edgecolor='black')
    plt.title('Histogramm')
    plt.xlabel('Time (s)')
    plt.ylabel('Number of Occurrences')
    plt.grid(True, alpha=0.5)
    plt.show()