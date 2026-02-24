import time
from eeg_api import eeghw_control
from src import EEGDeviceConfig, EEGDeviceMetadata
from eeg_api.src_eeg_api import LivePlotterChannelConfig, translation_func_adc, translation_func_dac

# General configuration for the EEG device
config = EEGDeviceConfig(
    com_name="AUTOCOM",  # Update with your serial port
    measure_duration=120,  # in seconds
    adc_pga_gain=1, # Gain for the ADC's Programmable Gain Amplifier (PGA)
    channel_mask=[1,1,1,1,1,1,1,1], # Mask to specify which channels are active (1 for active, 0 for inactive)
    sdo_driver_strength=3,
    adc_samplingrate= 1000,
    test_mode_enabled=False,
    adc_power_mode_high=True,
    error_header=False,
    reference_active_shielding=False,
    gain_instrument_amplifier=2
)
metadata = EEGDeviceMetadata(
    waveform_generator="ROHDE&SWARTZ MXO4",
    waveform_generator_frequency="10",
    waveform_generator_amplitude="500",
    waveform_type="Sine"
)


# Configuration for the live plotter. You can specify multiple channels to be visualized, each with its own configuration
# below is an example of how to visualize both the raw DAQ data and the player data (after translation). You can adjust the visualized_channel, name, lsl_layer_name, curve_color, and value_translation_func as needed for your specific use case.
# Note: The value_translation_func should be set to the appropriate translation function (e.g., translation_func_adc for raw DAQ data, translation_func_dac for player data) if you want to visualize the translated values. If you want to visualize the raw values, set value_translation_func to None.
config_plotter0 = [
    LivePlotterChannelConfig(visualized_channel=0, name="DAQ Data", lsl_layer_name="DAQ_Stream", curve_color="r", value_translation_func=translation_func_adc, window_width_sec=10.),
    LivePlotterChannelConfig(visualized_channel=0, name="Player Data", lsl_layer_name="PlayerData", curve_color="g", value_translation_func=translation_func_dac, window_width_sec=10.)
]
config_plotter1 = [
    LivePlotterChannelConfig(visualized_channel=0, lsl_layer_name="DAQ_Stream", curve_color="r", name="DAQ Data", value_translation_func=None, window_width_sec=2.)
]


if __name__ == "__main__":
    controller = eeghw_control.ApiEEGDeviceController(
        config=config,
        metadata=metadata,
        config_live_plotter=config_plotter0
    )
    controller.start_daq()
    #time.sleep(config.measure_duration)
    #controller.stop_daq()
