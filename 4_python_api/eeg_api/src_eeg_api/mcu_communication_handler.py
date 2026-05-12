from .mcu_communication_interface import InterfaceSerialUSB
from src.data_structures import EEGDeviceConfig, ErrorRegisterData
import serial, time
from .poti import calculate_requierd_resistor_value_for_amplification, calculate_poti_value

class McuCommunicationHandler:
    _interface: InterfaceSerialUSB
    _daq_config: EEGDeviceConfig
    def __init__(self, serial_handler: serial.Serial, config: EEGDeviceConfig) -> None:
        """Initializing the MCU Communication Handler

        Args:
            serial_handler (serial.Serial): Serial handler for communication
        """        
        self._interface = InterfaceSerialUSB(device =serial_handler, num_bytes_head=1, num_bytes_data=2)
        self._daq_config = config
    

    # ========== API METHODS ==========
    @property
    def total_num_of_each_transmission_bytes(self) -> int:
        """Returning the total number of bytes for each transmission, Important this is not suitable for the DAQ packets

        Returns:
            int: Number of total bytes
        """
        return self._interface.total_num_bytes
    

    @property
    def is_daq_active(self) -> bool:
        """Returning if DAQ is still running"""
        return self._get_system_state() == "DAQ"
    

    def do_reset(self) -> None:
        """Performing a Software Reset on the Platform"""
        self._write_wofb(1, 0)
        time.sleep(4)


    def echo(self, data: str) -> str:
        """Sending some characters to the device and returning the result

        Args:
            data (str): String with the data to be sent

        Raises:
            ValueError: If the device returns an error

        Returns:
            str: String with returned data from DAQ
        """
        do_padding = len(data) % self._interface.num_bytes == 1
        val = bytes()
        for chunk in self._interface.serialize_string(data, do_padding):
            ret = self._write_wfb(0, chunk)
            val += ret[1:]
            if ret[0] != 0x00:
                raise ValueError
        return self._interface.deserialize_string(val, do_padding)


    def get_system_clock_khz(self) -> int:
        """Getting the system clock of the device in kHz

        Raises:
            ValueError: If the device returns an error

        Returns:
            int: System clock in kHz
        """        
        ret = self._write_wfb(2, 0)
        if ret[0] != 0x02:
            raise ValueError
        return 10 * int.from_bytes(ret[1:], byteorder='little', signed=False)


    def get_pin_state(self) -> str:
        """Getting the current pin state of the device

        Returns:
            str: String with the current pin state
        """       
        ret = self._write_wfb(4, 0)[-1]
        return self.convert_pin_state(ret)
    

    def get_runtime_sec(self) -> float:
        """Returning the execution runtime of the device after last reset

        Raises:
            ValueError: If the device returns an error

        Returns:
            float: Float value with runtime in seconds
        """
        ret = self._write_wfb(5, 0, size=9)
        if ret[0] != 0x05:
            raise ValueError
        return 1e-6 * int.from_bytes(ret[1:], byteorder='little', signed=False)
    

    def get_firmware_version(self) -> str:
        """Returning the firmware version of the device

        Raises:
            ValueError: If the device returns an error

        Returns:
            str: String with firmware version
        """        
        ret = self._write_wfb(6, 0)
        if ret[0] != 0x06:
            raise ValueError
        return f"{ret[1]}.{ret[2]}"


    def enable_led(self) -> None:
        """Changing the state of the LED with enabling it"""
        self._write_wofb(7, 0)


    def disable_led(self) -> None:
        """Changing the state of the LED with disabling it"""
        self._write_wofb(8, 0)


    def toggle_led(self) -> None:
        """Changing the state of the LED with toggling it"""
        self._write_wofb(9, 0)


    def error_register(self) -> None:
        """Reading the error register of the device"""
        self._write_wofb(10, 0)
        register_values_packet = self._interface.read(19)
        if register_values_packet[0] != 0xaa or register_values_packet[-1] != 0xbb:
            raise ValueError("Invalid packet received from device")
        error_data = ErrorRegisterData( channel_0_error_status_register=register_values_packet[1],
                                        channel_1_error_status_register=register_values_packet[2],
                                        channel_2_error_status_register=register_values_packet[3],
                                        channel_3_error_status_register=register_values_packet[4],
                                        channel_4_error_status_register=register_values_packet[5],
                                        channel_5_error_status_register=register_values_packet[6],
                                        channel_6_error_status_register=register_values_packet[7],
                                        channel_7_error_status_register=register_values_packet[8],
                                        channel_0_1_dsp_error_register=register_values_packet[9],
                                        channel_2_3_dsp_error_register=register_values_packet[10],
                                        channel_4_5_dsp_error_register=register_values_packet[11],
                                        channel_6_7_dsp_error_register=register_values_packet[12],
                                        general_error_register_1=register_values_packet[13],
                                        general_error_register_2=register_values_packet[14],
                                        error_status_register_1=register_values_packet[15],
                                        error_status_register_2=register_values_packet[16],
                                        error_status_register_3=register_values_packet[17])
        return error_data


    def start_daq(self) -> None:
        """Starting the DAQ on the device"""
        self._write_wofb(11, 0)
    

    def stop_daq(self) -> None:
        """Stopping the DAQ on the device"""
        self._write_wofb(12, 0)


    def set_daq_settings(self) -> None:
        """Wirteting the DAQ settings to the device and updating the registers"""        
        self._set_pga_gain(self._daq_config.adc_pga_gain)
        self._set_channel_mask(self._daq_config.channel_mask)
        self._set_sdo_driver_strength(self._daq_config.sdo_driver_strength)
        self._set_sampling_rate_sps(self._daq_config.adc_samplingrate)
        self._set_test_mode(self._daq_config.test_mode_enabled)
        self._set_power_mode(self._daq_config.adc_power_mode_high)
        self._set_header_type(self._daq_config.error_header)
        
        self._update_registers()

        
    def set_shielding_settings(self) -> None:
        """Writing the shielding settings to the device and update the GPIO pins"""        
        self._set_reference_active_shielding(self._daq_config.reference_active_shielding)


    def set_gain_instrument_amplifier(self, position_poti: int) -> None:
        """Writing the gain settings for the instrumentation amplifier to the device and update the potentiometer values"""        
        self._set_poti_value(position_poti)


    #  ========== INTERNAL METHODS ==========
    def _update_registers(self) -> None:
        """Updating the registers of the device"""
        self._write_wofb(13, 0)


    def _set_pga_gain(self, gain: int) -> None:
        """Setting the PGA Gain of the ad7779

        Args:
            gain (int): Gain value to be set, must be one of [1, 2, 4, 8]

        Raises:
            ValueError: If the gain value is not valid
        """        
        if gain not in [1, 2, 4, 8]:
            raise ValueError("Invalid gain value. Must be one of [1, 2, 4, 8].")
        self._write_wofb(14, gain)


    def _set_channel_mask(self, channel_mask: list[int]) -> None:
        """Setting the channel mask for the ad7779

        Args:
            channel_mask (list[int]): List with 8 elements, each element is either 0 (disabled) or 1 (enabled)

        Raises:
            ValueError: If the channel mask is not valid
        """        
        if len(channel_mask) != 8 or any(ch not in [0,1] for ch in channel_mask):
            raise ValueError("Invalid channel mask. Must be a list of 8 elements with values 0 or 1.")
        mask_value = sum(bit << idx for idx, bit in enumerate(channel_mask))
        self._write_wofb(15, mask_value)


    def _set_sdo_driver_strength(self, strength: int) -> None:
        """Setting the SDO driver strength for the ad7779

        Args:
            strength (int): Strength value to be set, must be one of [0, 1, 2, 3] 0 for normal, 1 for strong, 2 for weak, 3 for extreme

        Raises:
            ValueError: If the strength value is not valid
        """        
        if strength not in [0, 1, 2, 3]:
            raise ValueError("Invalid SDO driver strength. Must be one of [0, 1, 2, 3].")
        self._write_wofb(16, strength)


    def _set_sampling_rate_sps(self, sps: int) -> None:
        """Setting the sampling rate in samples per second (SPS) for the device

        Args:
            sps (int): Sampling rate in samples per second

        Raises:
            ValueError: If the sampling rate is not valid
        """        
        if sps > 160000 or sps < 0:
            raise ValueError("Invalid sampling rate. Must be between 0 and 160000 SPS.")
        self._write_wofb(17, sps)


    def _set_test_mode(self, enabled: bool) -> None:
        """Setting the test mode of the device

        Args:
            enabled (bool): True to enable test mode, False to disable
        """        
        self._write_wofb(18, 1 if enabled else 0)
    

    def _set_power_mode(self, high_power: bool) -> None:
        """Setting the power mode of the device

        Args:
            high_power (bool): True for high power mode, False for low power mode
        """        
        self._write_wofb(19, 1 if high_power else 0)


    def _set_header_type(self, enabled: bool) -> None:
        """Setting the header type of the device

        Args:
            enabled (bool): True to enable the Errorheader, False to get the CRC header
       """        
        self._write_wofb(20, 1 if enabled else 0)


    def _set_reference_active_shielding(self, enabled: bool) -> None:
        """Setting the active shielding for the reference

        Args:
            enabled (bool): True to enable active shielding on reference, False to disable and tight to GND
        """        
        self._write_wofb(21, 1 if enabled else 0)


    def _set_poti_value(self, poti_value: int) -> None:
        """Setting the potentiometer value for all channels

        Args:
            poti_value (int): Potentiometer value to be set
        """        
        self._write_wofb(22, poti_value)


    def _write_wofb(self, head: int, data: int, size: int=0) -> None:
        """Write data to the device, and convert without feedback, using the deployed interface

        Args:
            head (int): Value for the head byte
            data (int): Value for the data bytes
            size (int, optional): Size of the data. Defaults to 0.
        """        
        self._interface.write_wofb(
            data=self._interface.convert(head, data),
        )
    

    def _write_wfb(self, head: int, data: int, size: int=0) -> bytes:
        """Write data, and convert with feedback, to the device

        Args:
            head (int): Value for the head byte
            data (int): Value for the data bytes
            size (int, optional): Size of the data. Defaults to 0.

        Returns:
            bytes: Returned bytes from the device
        """        
        return self._interface.write_wfb(
            data=self._interface.convert(head, data),
            size=size
        )
    
    
    def _get_system_state(self) -> str:
        """Getting the current system state of the device

        Returns:
            str: String with the current system state
        """        
        ret = self._write_wfb(3, 0)[-1]
        return self.convert_system_state(ret)
    

    #  ========== STATIC METHODS ==========
    @staticmethod
    def convert_pin_state(state: int) -> str:
        """_summary_

        Args:
            state (int): _description_

        Returns:
            str: _description_
        """    
        if state == 0:
            return 'NONE'
        else:
            # TODO: Implement logic for several pins
            return 'LED_USER'


    @staticmethod
    def convert_system_state(state: int) -> str:
        """Function for converting the int Value into the System state

        Args:
            state (int): Integer value of the system state

        Raises:
            ValueError: If the Integer value is not valid

        Returns:
            str: String with the system state
        """
        state_name = ["ERROR", "RESET", "INIT", "IDLE", "TEST", "DAQ"]
        if not 0 <= state < len(state_name):
            raise ValueError(f'Invalid pin state: {state}')
        return state_name[state]