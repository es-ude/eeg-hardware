from dataclasses import dataclass
import numpy as np


@dataclass
class EEGDeviceConfig:
    """Dataclass for handling EEG Device Configuration Parameters
    Attributes:
        com_name: str Name of the COM port for serial connection, pass "AUTOCOM" to look automatically for the device
        measure_duration: int Total duration of the measurement in seconds
        channel_mask: list with all channels active (1) or inactive (0), e.g. [1,1,1,1,1,1,1,1] for 8 channels
        adc_samplingrate: int ADC sampling rate in Hz
        adc_power_mode_high: bool True for high power mode, False for low power mode
        reference_active_shielding: bool True to enable active shielding on reference, False to disable and tight to GND
        gain_instrument_amplifier: Gain value for the instrument amplifier; this value is applied to each channel
    """  
    com_name: str
    measure_duration: int
    adc_pga_gain: int
    channel_mask: list
    sdo_driver_strength: int
    adc_samplingrate: int
    test_mode_enabled: bool
    adc_power_mode_high: bool
    error_header: bool
    reference_active_shielding: bool
    gain_instrument_amplifier: float


@dataclass
class EEGDeviceMetadata:
    """Dataclass for handling EEG Device Configuration Parameters
    Attributes:
        measurment_duration: int Total duration of the measurement in seconds
        waveform_generator: str Type of waveform generator
        waveform_generator_frequency: str Frequency of the waveform generator
        waveform_generator_amplitude: str Amplitude of the waveform generator
        waveform_type: str Type of the waveform
    """
    waveform_generator: str
    waveform_generator_frequency: str
    waveform_generator_amplitude: str
    waveform_type: str


@dataclass
class TransientMetadata:
    """Dataclass for handling metadata from the .h5 file.
    Attributes:
        measurment_duration: int Total duration of the measurement in seconds
        adc_samplingrate: int ADC sampling rate in Hz
        channel_mask: list with all channels active (1) or inactive (0)
        waveform_generator: str Type of waveform generator
        waveform_generator_frequency: str Frequency of the waveform generator
        waveform_generator_amplitude: str Amplitude of the waveform generator
        waveform_type: str Type of the waveform
    """    
    measurement_duration: int
    adc_samplingrate: int
    channel_mask: list
    waveform_generator: str
    waveform_generator_frequency: str
    waveform_generator_amplitude: str
    waveform_type: str


@dataclass
class TransientData:
    """Dataclass for handling measured transient data
    Attributes:
        timestamps: Numpy array in seconds from start of measurement
        rawdata:    Numpy array data points in volts
        sampling_rate:  Float with sampling rate in Hz
        channels:   List containing a list with all channels active (1) or inactive (0)
    """
    timestamps: np.ndarray
    rawdata: np.ndarray
    sampling_rate: float
    error_flags: list
    channels: list


@dataclass
class ErrorRegisterData:
    """Dataclass for handling error register data from the device
    Attributes:
        channel_0_error_status_register: int 
        channel_1_error_status_register: int 
        channel_2_error_status_register: int
        channel_3_error_status_register: int
        channel_4_error_status_register: int
        channel_5_error_status_register: int
        channel_6_error_status_register: int
        channel_7_error_status_register: int
        channel_0_1_dsp_error_register: int
        channel_2_3_dsp_error_register: int
        channel_4_5_dsp_error_register: int
        channel_6_7_dsp_error_register: int
        general_error_register_1: int
        general_error_register_2: int
        error_status_register_1: int
        error_status_register_2: int
        error_status_register_3: int
    """
    channel_0_error_status_register: int
    channel_1_error_status_register: int
    channel_2_error_status_register: int
    channel_3_error_status_register: int
    channel_4_error_status_register: int
    channel_5_error_status_register: int
    channel_6_error_status_register: int
    channel_7_error_status_register: int
    channel_0_1_dsp_error_register: int
    channel_2_3_dsp_error_register: int
    channel_4_5_dsp_error_register: int
    channel_6_7_dsp_error_register: int
    general_error_register_1: int
    general_error_register_2: int
    error_status_register_1: int
    error_status_register_2: int
    error_status_register_3: int