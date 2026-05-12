import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from analysis.load_data import load_dut_data

from elasticai.hw_measurements import TransientData, TransformSpectrum
from elasticai.hw_measurements.plots import get_plot_color, get_font_size, scale_auto_value, save_figure
from elasticai.hw_measurements.process import load_transient_data, do_fft


def get_local_minimum(signal: np.ndarray) -> int:
    mask = (signal[1:-1] < signal[:-2]) & (signal[1:-1] < signal[2:])
    indices = np.where(mask)[0] + 1
    if len(indices) > 0:
        return indices[0]-1
    else:
        return 0


def plot_transient(data_dut: TransientData, data_mxo: TransientData, delta_x: int, path2file: str="", file_name: str="", show_plots: bool=False, gain_dut: float=1.0) -> None:
    """Analyze and plot the comparison between DUT and MXO4 transient data

    Args:
        data_dut (TransientData): DUT transient data
        data_mxo (TransientData): MXO4 transient data
        delta_x (int): Offset for x-axis alignment
        path2file (str, optional): Path to save the figure. Defaults to "".
        file_name (str, optional): Name of the file for saving the figure. Defaults to "".
        show_plots (bool, optional): Whether to show the plots. Defaults to False.
        gain_dut (float, optional): Gain for DUT. Defaults to 1.0.
    """
    downsample_factor = 2
    gain_input = 25.
    gain = gain_input * gain_dut
    xstart = get_local_minimum(np.diff(data_dut.rawdata[0, :])) + delta_x
    xstop = xstart + np.argwhere(data_dut.timestamps >= data_mxo.timestamps[-1]).flatten()[0]
    offsety = [(data.max()+data.min())/2 for data in data_mxo.rawdata]

    # --- Transient subplot
    scale_y, unit_y = scale_auto_value(data_mxo.rawdata)
    fig, axs = plt.subplots(1, 1, sharex=False, sharey=False)
    axs.plot(data_dut.timestamps[xstart:xstop]-data_dut.timestamps[xstart], scale_y/gain * data_dut.rawdata[xstart:xstop, 0], linewidth=2.0, color=get_plot_color(0), label="norm. ADC output")
    axs.plot(data_mxo.timestamps[::downsample_factor], scale_y/gain_input * (data_mxo.rawdata[0,::downsample_factor]-offsety[0]), linewidth=1.5, color=get_plot_color(1), label="Generator")

    axs.set_xlabel("Time [s]", fontsize=get_font_size())
    axs.set_ylabel(f"Voltage [{unit_y}V]", fontsize=get_font_size())
    axs.set_xlim([0., 1.])
    axs.legend(loc="best")
    axs.grid()
    axs.tick_params(axis='both', labelsize=get_font_size() - 1)
    plt.tight_layout()

    if path2file:
        save_figure(fig, path2file, f"{file_name}_transient", formats=["eps", "pdf", "svg"])
    if show_plots:
        plt.show(block=True)


def plot_transient_comparison(data_dut: TransientData, data_mxo: TransientData, delta_x: int, path2file: str="", file_name: str="", show_plots: bool=False, gain_dut: float=1.0) -> None:
    """Analyze and plot the comparison between DUT and MXO4 transient data

    Args:
        data_dut (TransientData): DUT transient data
        data_mxo (TransientData): MXO4 transient data
        delta_x (int): Offset for x-axis alignment
        path2file (str, optional): Path to save the figure. Defaults to "".
        file_name (str, optional): Name of the file for saving the figure. Defaults to "".
        show_plots (bool, optional): Whether to show the plots. Defaults to False.
        gain_dut (float, optional): Gain for DUT. Defaults to 1.0.
    """    
    downsample_factor = 2
    gain_input = 25.
    gain = gain_input * gain_dut
    xstart = get_local_minimum(np.diff(data_dut.rawdata[0, :])) + delta_x
    xstop = xstart + np.argwhere(data_dut.timestamps >= data_mxo.timestamps[-1]).flatten()[0]
    offsety = [(data.max()+data.min())/2 for data in data_mxo.rawdata]

    # --- Transient subplot
    scale_y, unit_y = scale_auto_value(data_mxo.rawdata)
    fig, axs = plt.subplots(2, 1, sharex=False, sharey=False)
    axs[0].plot(data_dut.timestamps[xstart:xstop]-data_dut.timestamps[xstart], scale_y/gain * data_dut.rawdata[xstart:xstop, 0], color=get_plot_color(0), label="norm. ADC output")
    axs[0].plot(data_mxo.timestamps[::downsample_factor], scale_y/gain_input * (data_mxo.rawdata[0,::downsample_factor]-offsety[0]), color=get_plot_color(1), label="Generator")
    axs[0].plot(data_mxo.timestamps[::downsample_factor], scale_y/gain_input * (data_mxo.rawdata[0,::downsample_factor]-offsety[0]), color=get_plot_color(2), label="Shielding")

    axs[0].set_xlabel("Time [s]", fontsize=get_font_size())
    axs[0].set_ylabel(f"Voltage [{unit_y}V]", fontsize=get_font_size())
    axs[0].set_xlim([0., 1.])
    axs[0].legend(loc="best")

    # --- Spectral subplot
    spec_adc: TransformSpectrum = do_fft(
        y=data_dut.rawdata[:,0]/gain/2,
        fs=data_dut.sampling_rate,
        method_window=''
    )
    spec_elec: TransformSpectrum = do_fft(
        y=np.tile(data_mxo.rawdata[0,:]/gain_input/2, 10),
        fs=data_mxo.sampling_rate,
        method_window=''
    )
    axs[1].semilogx(spec_elec.freq, scale_y * spec_elec.spec, color=get_plot_color(1), label="Generator")
    axs[1].semilogx(spec_adc.freq, scale_y * spec_adc.spec, color=get_plot_color(0), label="norm. ADC output")
    axs[1].set_xlabel("Frequency [Hz]", fontsize=get_font_size())
    axs[1].set_ylabel(f"Amplitude [{unit_y}V]", fontsize=get_font_size())
    axs[1].set_xlim([5e0, 2e2])

    for ax in axs:
        ax.grid()
        ax.tick_params(axis='both', labelsize=get_font_size() - 1)
    plt.tight_layout()
    if path2file:
        save_figure(fig, path2file, f"{file_name}_comparison", formats=["eps", "pdf", "svg"])
    if show_plots:
        plt.show(block=True)


def plot_histogram(data_dut: TransientData, path2file: str="", file_name: str="", show_plots: bool=False) -> None:
    data_in = np.diff(data_dut.timestamps)
    scale_y, unit_y = scale_auto_value(data_in)

    fig = plt.figure()
    plt.hist(scale_y * data_in, bins=100, color=get_plot_color(0))
    plt.xlabel(f"Sampling Period [{unit_y}s]", fontsize=get_font_size())
    plt.ylabel(f"Bins", fontsize=get_font_size())

    plt.grid()
    plt.tick_params(axis='both', labelsize=get_font_size() - 1)

    plt.tight_layout()
    if path2file:
        save_figure(fig, path2file, f"{file_name}_hist", formats=["eps", "pdf", "svg"])
    if show_plots:
        plt.show(block=True)


def analyse_data(path: Path, subfolder_name: str, file_name_mxo4: str, delta_x: int, show_last_plot: bool=False, gain_dut: float=1.0) -> None:
    if not subfolder_name == "":
        final_path = path / subfolder_name
    else:
        final_path = path

    data0, file0 = load_dut_data(final_path, load_case=0, do_postprocessing=False, do_plot=False)
    data1 = load_transient_data(final_path / file_name_mxo4)

    plot_transient(
        data_dut=data0,
        data_mxo=data1,
        delta_x=delta_x,
        path2file=str(final_path.absolute()),
        file_name=file0.stem,
        show_plots=False,
        gain_dut=gain_dut,
    )
    plot_histogram(
        data_dut=data0,
        path2file=str(final_path.absolute()),
        file_name=file0.stem,
        show_plots=show_last_plot
    )


def analyse_coupling_effects(path: Path, subfolder_name: str, file_name_mxo4: str, delta_x: int, show_last_plot: bool=False, gain_dut: float=1.0) -> None:
    """Analyze coupling effects between DUT and MXO4 measurement

        Required file structure:
            : Masterpath: 
                : subfolder_name
                    example_data.h5
                    file_name_mxo4.h5
    
    Args:
        path (Path): Master path to data
        subfolder_name (str): Subfolder name within the master path
        file_name_mxo4 (str): File name of the MXO4 data
        delta_x (int): Offset for x-axis alignment
        show_last_plot (bool, optional): Whether to show the last plot. Defaults to False.
        gain_dut (float, optional): Gain for DUT. Defaults to 1.0.
    """    
    if not subfolder_name == "":
        final_path = path / subfolder_name
    else:
        final_path = path
    
    data0, file0 = load_dut_data(final_path, load_case=0,do_postprocessing=False, do_plot=False)
    data1 = load_transient_data(final_path / file_name_mxo4)

    plot_transient_comparison(
        data_dut=data0,
        data_mxo=data1,
        path2file=str(final_path.absolute()),
        file_name=file0.stem,
        show_plots=show_last_plot,
        delta_x=delta_x,
        gain_dut=gain_dut
    )


def analyse_coupling_effects_fake(path: Path, subfolder_name: str, delta_x: int, show_last_plot: bool=False, gain_dut: float=1.0) -> None:
    data0, file0 = load_dut_data(path / subfolder_name, 0, do_postprocessing=False)

    random_phase = 0.5* np.pi + np.pi* np.random.randn(1)
    fake_signal = -740e-3* np.sin(2*np.pi*10*data0.timestamps)
    fake_signal -= 470e-3* np.sin(2*np.pi*50*data0.timestamps + random_phase)
    fake_signal -= 60e-3* np.sin(2*np.pi*100*data0.timestamps + random_phase)
    fake_signal += 1e-3 * np.random.randn(*fake_signal.shape)
    data2 = TransientData(
        rawdata=np.expand_dims(fake_signal, axis=0),
        timestamps=data0.timestamps,
        sampling_rate=data0.sampling_rate,
        channels=data0.channels
    )
    file1 = list((path / subfolder_name).glob("*.h5"))
    data1 = load_transient_data(file1[0])

    plot_transient_comparison(
        data_dut=data2,
        data_mxo=data1,
        path2file=str((path / subfolder_name).absolute()),
        file_name=file0.stem,
        show_plots=show_last_plot,
        delta_x=delta_x,
        gain_dut=gain_dut
    )


if __name__ == '__main__':
    master_path = Path("./../../2_charac/version_01-2/")
    subfolder = "EEG_Dummy-Messung"

    if len(list((master_path / subfolder).absolute().glob("*_data.h5"))) == 0:
        raise FileNotFoundError("No data found")

    file_mxo4 = list((master_path / subfolder).absolute().glob("*_mxo4.h5"))
    if len(file_mxo4) == 0:
        raise FileNotFoundError("No MXO4 data found")

    analyse_data(
    #analyse_coupling_effects(
        path=master_path,
        subfolder_name=subfolder,
        file_name_mxo4=str(file_mxo4[0]),
        delta_x=348,
        show_last_plot=True,
        gain_dut=1.
    )
    # analyse_coupling_effects_fake(master_path / subfolder, "shielding_gnd", delta_x=8, show_last_plot=True)
