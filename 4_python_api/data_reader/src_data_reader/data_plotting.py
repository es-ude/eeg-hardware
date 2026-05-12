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

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(dt, bins=2000, color='black', edgecolor='black')
    #ax.set_yscale("log")
    fig.suptitle('Histogramm')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Number of Occurrences')
    ax.grid(True, alpha=0.5)
    plt.setp(ax.get_xticklabels(), fontsize=12, fontweight='bold')
    plt.setp(ax.get_yticklabels(), fontsize=12, fontweight='bold')
    ax.set_xlabel("Time (s)", fontsize=14, fontweight='bold')
    ax.set_ylabel("Number of Occurrences", fontsize=14, fontweight='bold')
    fig.suptitle("Histogramm Interrupt", fontsize=16, fontweight='bold')
    plt.show()
    fig.savefig("histogramm.pdf", format="pdf", bbox_inches="tight")