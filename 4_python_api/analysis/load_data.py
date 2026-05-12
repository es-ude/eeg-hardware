import numpy as np
from pathlib import Path
from data_reader.reader import EEGDataReader
from src.data_structures import TransientData as EEGData

from elasticai.hw_measurements import TransientData, FrequencyResponse
from elasticai.hw_measurements.plots import plot_transient_data, plot_fra_data
from elasticai.hw_measurements.process.mxo4x import load_fra_data
from elasticai.hw_measurements.template.noise import extract_noise_metrics


def load_dut_data(masterpath: Path, load_case: int, do_postprocessing: bool=False, do_plot: bool=False, start_time_sec: float=0.0) -> tuple[EEGData, Path]:
    dut = EEGDataReader(path=masterpath, load_case=load_case)
    if do_postprocessing:
        dut.post_process_error_flags()
    data0: EEGData = dut.get_data()
    if do_plot:
        dut.plot_transient_data(data0, channel_to_plot=0)
    start_pos = int(np.argwhere(data0.timestamps >= start_time_sec).flatten()[0])

    return TransientData(
        rawdata=data0.rawdata[start_pos:, :],
        timestamps=data0.timestamps[start_pos:],
        channels=data0.channels,
        sampling_rate=data0.sampling_rate
    ), dut.get_path2file()


def analyse_harmonic_dut(path: Path, selected_channel: int, show_data_plot:bool=False, show_last_plot: bool=False) -> None:
    """Analyse of the harmonic distortion measurement of the DUT

        Required file structure:
            : Masterpath: 
                : Harmonic
                    example_adc.h5

    Args:
        path (Path): Master path to the measurement folder
        selected_channel (int): channel to be analysed
        show_data_plot (bool, optional): whether to plot the transient signal of the raw data
        show_last_plot (bool, optional): Whether to show the last plot. Defaults to False.
    """
    data, file = load_dut_data(
        masterpath=path,
        load_case=0,
        do_postprocessing=False,
        do_plot=show_data_plot
    )
    raw_1d = data.rawdata[:,selected_channel].T
    mean_1d = np.mean(raw_1d)
    noise_1d = raw_1d - mean_1d
    raw_2d = np.expand_dims(noise_1d, axis=0)

    data = TransientData(
        rawdata=raw_2d,
        timestamps=data.timestamps,
        channels=np.array([1]),
        sampling_rate=data.sampling_rate
    )
    plot_transient_data(
        data=data,
        file_name=file.stem,
        path2save=str(file.parent),
        show_plot=show_last_plot,
        xzoom=[10000, 16000]
    )

def analyse_fra_mxo4(path: Path, show_last_plot: bool=False) -> None:
    list_files = list((path / "FRA").glob("*.csv"))
    for file in list_files:
        data = load_fra_data(path2file=file)

        data_new = FrequencyResponse(
            freq=data.freq,
            phase=data.phase,
            gain=data.gain + 20*np.log10(1.2),
        )
        plot_fra_data(
            data=data_new,
            num_pol=1,
            path2save=str(file.parent),
            file_name=file.stem,
            show_plot=show_last_plot and file == list_files[-1],
        )


def analyse_noise_combi(path: Path, channel_noise_adc: int, channel_noise_afe: int, do_postprocessing: bool=False, show_last_plot: bool=False, gain_afe: float=74.) -> None:
    """Analyse combined noise measurement from ADC and AFE

    Required file structure:
        : Masterpath: 
            : Noise_ADC
                example_adc.h5
            : Noise_AFE
                example_afe.h5
    Args:
        path (Path): Path to the master folder
        channel_noise_adc (int): Selected channel for ADC noise
        channel_noise_afe (int): Selected channel for AFE noise
        do_postprocessing (bool, optional): Whether to perform postprocessing. Defaults to True.
        show_last_plot (bool, optional): Whether to show the last plot. Defaults to False.
        gain_afe (float): Floating value with the gain value

    """
    data0, file0 = load_dut_data(masterpath= path / "Noise_ADC", load_case=0, do_postprocessing=do_postprocessing, do_plot=False)
    data1, file1 = load_dut_data(masterpath= path / "Noise_AFE", load_case=-1, do_postprocessing=do_postprocessing, do_plot=False)

    min_size = int(np.min([data0.timestamps.size, data1.timestamps.size]))

    data_new = np.array([
        data0.rawdata[:min_size, channel_noise_adc],            # Kanal 1: ADC
        data1.rawdata[:min_size, channel_noise_afe] / gain_afe  # Kanal 2: AFE (normiert)
    ])
    data = TransientData(
        rawdata=data_new,
        timestamps=data0.timestamps[0:min_size],
        channels=[r"only ADC, $v_u$=1", r"AFE, $v_u$="+f"{gain_afe}"],
        sampling_rate=data0.sampling_rate,
    )
    dut = extract_noise_metrics(
        data=data,
        exclude_channels=[],
        scale_adc=1.0001,
        path2file=path,
        show_plots=show_last_plot
    )
    dut.extract_noise_rms_specific(0.5, 100.)


if __name__ == "__main__":
    master_path = Path("/Users/nickskill/Library/CloudStorage/OneDrive-Persönlich/Uni/Master/Masterarbeit/Bode_diagramm_hardware_v2")
    load_case = 0
    channel_adc = 0
    channel_afe = 0

    analyse_fra_mxo4(path=master_path, show_last_plot=False)
    #analyse_harmonic_dut(path=master_path, selected_channel=0, show_last_plot=False)

    """analyse_noise_combi(
        path=master_path,
        channel_noise_adc=channel_adc,
        channel_noise_afe=channel_afe,
        do_postprocessing=True,
        show_last_plot=True
    )"""