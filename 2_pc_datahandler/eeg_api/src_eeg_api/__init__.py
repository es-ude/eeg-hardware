from .lsl_handler import LSLHandler
from .serial_handler import SerialHandler
from .data_processing import extract_channel_data, extract_error_flags
from .h5_handler import H5Handler
from .live_visualizer import LivePlotter, start_live_plotter, LivePlotterChannelConfig, translation_func_adc, translation_func_dac
from .mcu_communication_handler import McuCommunicationHandler
from .poti import PotiConfig, generate_poti_config, calculate_requierd_resistor_value_for_amplification, calculate_poti_value, calculate_gain