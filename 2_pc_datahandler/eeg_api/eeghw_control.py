from src import SerialHandler, LSLHandler, H5Handler, McuCommunicationHandler, LivePlotter, LivePlotterChannelConfig, PotiConfig, generate_poti_config, start_live_plotter, extract_channel_data, extract_error_flags, calculate_requierd_resistor_value_for_amplification, calculate_poti_value, calculate_gain
from src import EEGDeviceConfig, EEGDeviceMetadata, ErrorRegisterData
import serial, threading, queue, time
from datetime import datetime
from pylsl import StreamOutlet, resolve_byprop, StreamInlet, proc_threadsafe
import multiprocessing
import numpy as np

#Define packet length
PACKET_LENGTH = 38

# Define Characteristics of the different data frames
characteristics_dataframes = {"adc_data_24": 0x00,
                              "sensor_data": 0x01,
                              }


class ApiEEGDeviceController:
    _eeg_device_config: EEGDeviceConfig
    _adc_samplingrate: int
    _metadata: EEGDeviceMetadata

    _packet_length: int
    _expected_packet_number: int
    _start_time: time
    _stop_time: time

    _poti_config: PotiConfig

    _running: bool
    _recording_name: str

    _deployed_data_frames: list
    _deployed_serial_connection: serial.Serial
    _deployed_daq_outlet: StreamOutlet
    deployed_mcu_communication_handler: McuCommunicationHandler
    _config_live_plotter: list[LivePlotterChannelConfig]

    def __init__(self, config: EEGDeviceConfig, metadata: EEGDeviceMetadata, config_live_plotter: list[LivePlotterChannelConfig]=None) -> None:
        """Initialize the SerialDataHandler with serial connection and thread management / subprocess mangagement also handles the DAQ settings on the device side and initializes the LSL outlet for streaming data

        Args:
            config (EEGDeviceConfig): Configuration parameters for the EEG device
            metadata (EEGDeviceMetadata): Metadata information for the measurement
            config_live_plotter (list[LivePlotterChannelConfig], optional): Configuration for live plotter channels. Defaults to None.
        """
        self._eeg_device_config = config
        self._adc_samplingrate = config.adc_samplingrate
        self._metadata = metadata
        self._config_live_plotter = config_live_plotter
        self._packet_length = PACKET_LENGTH
        self._expected_packet_number = None 
        self._start_time = None  # To record the start time of data acquisition
        self._stop_time = None   # To record the stop time of data acquisition
        self._running = False    # Flag to control thread execution
        self._recording_name = datetime.now().strftime("Measurement_hardware_eeg%Y%m%d_%H%M%S")


        self._poti_config = generate_poti_config(config.gain_instrument_amplifier)
        
        self._poti_config.calculated_resistor_value = calculate_requierd_resistor_value_for_amplification(self._poti_config.gain)
        self._poti_config.poti_value, self._poti_config.actual_resistor_value = calculate_poti_value(self._poti_config.calculated_resistor_value)
        self._poti_config.actual_gain_value = calculate_gain(self._poti_config.actual_resistor_value)

        self._deployed_data_frames = characteristics_dataframes
        self._deployed_serial_connection = SerialHandler(com_name= config.com_name, baudrate=115200, time_out=1).get_serial_connection
        self._deployed_daq_outlet = LSLHandler(name="DAQ_Stream", sampling_rate=self._adc_samplingrate).create_lsl_outlet_daq

        self.deployed_mcu_communication_handler = McuCommunicationHandler(serial_handler=self._deployed_serial_connection, config= self._eeg_device_config)
        self.deployed_mcu_communication_handler.set_daq_settings() # handles the DAQ settings on the device
        self.deployed_mcu_communication_handler.set_shielding_settings() # handles the GPIO pins for shielding electrodes and reference
        self.deployed_mcu_communication_handler.set_gain_instrument_amplifier(self._poti_config.poti_value) # handles the gain settings for the instrumentation amplifier on the device

    # ========== API METHODS ==========
    def output_daq_error_register(self) -> ErrorRegisterData:
        """Get the latest error register data from the device

        Returns:
            ErrorRegisterData: Dataclass containing error register information for both channels
        """
        return self.deployed_mcu_communication_handler.error_register()


    def start_daq(self) -> bool:
        """Start the data acquisition threads

        Returns:
            bool: True if threads started successfully, False if already running
        """
        if self._running:
            print("Already running!")
            return False
        self._running = True


        self.read_process_thread = threading.Thread(
            target=self._read_and_process_serial_data,
            name="SerialReadProcess",
            daemon=True
        )

        self.writer_thread = threading.Thread(
            target=self._write_to_h5_file,
            name="FileWriter",
            daemon=True
        )

        self.writer_thread.start()
        while not self._deployed_daq_outlet.have_consumers():
            print("Waiting for LSL consumers to connect...")
            time.sleep(0.001)
        self.deployed_mcu_communication_handler.start_daq() # Start DAQ on the device side

        if self._config_live_plotter is not None:
            self.live_plotter_process = multiprocessing.Process(target=start_live_plotter, kwargs={"config": self._config_live_plotter})
            self.live_plotter_process.start()

        self.read_process_thread.start()
        self._start_time = time.time()
        return True


    def stop_daq(self) -> bool:
        """Stop the data acquisition threads

        Returns:
            bool: True if threads stopped successfully
        """
        self._running = False

        self.deployed_mcu_communication_handler.stop_daq() # Stop DAQ on the device side
        self._stop_time = time.time()
        
        time.sleep(0.5)  # Give threads time to exit their loops
        if self.read_process_thread is not None:
            self.read_process_thread.join()
        if self.writer_thread is not None:
            self.writer_thread.join()
        if self.live_plotter_process.is_alive():
            self.live_plotter_process.terminate()
        print("Threads stopped.")
        return True


    #  ========== INTERNAL METHODS ==========
    @property
    def _thread_frame_datatype(self) -> np.dtype:
        return np.dtype([
            ("head", "u1"),  # 1 Byte unsigned
            ("frame_id", "u1"),  # 1 Byte unsigned
            ("index", "u1"),  # 1 Byte unsigned
            ("timestamp", "<u8"),  # 8 Byte unsigned
            ("active_channels", "u1"),  # 1 Byte unsigned
            ("alert", "u1",),  # 1 Byte unsigned
            ("channel_values", "u1", (24,)),  # 24 Byte unsigned
            ("tail", "u1"),  # 1 Byte unsigned
        ])


    def _read_and_process_serial_data(self) -> None:
        """Read data from the serial connection and process packets"""
        while self._running:
            try:
                batch = self._deployed_serial_connection.read(PACKET_LENGTH)
            
                if len(batch) != PACKET_LENGTH:
                    print("Incomplete packet received, skipping")
                    raise Exception
                frames = np.frombuffer(batch, dtype= self._thread_frame_datatype)

                if not (frames['head'] == 0xAA) & (frames['tail'] == 0xBB):
                    print("Invalid packet header or tail, skipping")
                    raise Exception
                if not self._check_packet_number(int(frames["index"][0])):
                    print("Packet number check failed, skipping")
                    raise Exception

                data_list = extract_channel_data(frames["channel_values"][0])
                error_flag_list = extract_error_flags(frames["alert"][0])
                packet_to_send = data_list + error_flag_list + [frames["timestamp"][0]]

                self._deployed_daq_outlet.push_sample(packet_to_send, pushthrough=True)
            except Exception:
                continue
    

    def _check_packet_number(self, packet_index) -> bool:
        """Function to check the packet number for continuity, Check for lost packets

        Returns:
            bool: True if packet number is as expected, False otherwise
        """        
        if self._expected_packet_number == None:
            self._expected_packet_number = (packet_index + 1) % 256 # Wrap around at 256
            return True
        elif packet_index != self._expected_packet_number:
            print(f"Packet number mismatch: expected {self._expected_packet_number}, got {packet_index}")
            self._expected_packet_number = (packet_index + 1) % 256 # Wrap around at 256
            return False
        self._expected_packet_number = (self._expected_packet_number + 1) % 256  # Wrap around at 256
        return True


    def _init_h5_file_writer(self) -> H5Handler:
        """Initialize H5 file writer

        Returns:
            H5Handler: H5 file handler instance
        """        
        return H5Handler(recording_name=self._recording_name, metadata= self._metadata, eeg_device_config= self._eeg_device_config, poti_values= self._poti_config)    


    def _write_to_h5_file(self) -> None:
        """Write data from the queue to H5 file in chunks"""
        deployed_h5_writer = self._init_h5_file_writer()
        streams = resolve_byprop("type", "custom_daq")
        data_stream = StreamInlet(streams[0],
                                  max_buflen= 60,
                                  max_chunklen= 1024,
                                  recover=True,
                                  processing_flags=proc_threadsafe)
        timeout = (1 / self._adc_samplingrate)*1e-2
        max_samples = (self._adc_samplingrate /50) if self._adc_samplingrate >50 else 10
        while self._running:
            data, timestamp = data_stream.pull_chunk(timeout=timeout)
            if data:
                deployed_h5_writer.append_data_ad7779(timestamps =[row[-1] for row in data], 
                                                      measurements =[row[:8] for row in data], 
                                                      alerts=[row[8:-1] for row in data])
            
        # make sure to close the H5 file when stopping
        print(f"Total samples written to file: {deployed_h5_writer.get_file_length}")
        deployed_h5_writer.close_h5_file()