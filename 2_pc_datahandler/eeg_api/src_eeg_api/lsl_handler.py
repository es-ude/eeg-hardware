from pylsl import StreamInfo, StreamOutlet, FOREVER, IRREGULAR_RATE, cf_int64, cf_int32

class LSLHandler:
    def __init__(self, name, sampling_rate: float= IRREGULAR_RATE):
        """Class to handle LSL stream creation and management for EEG DAQ data"""
        self._name = name
        self._sampling_rate = sampling_rate


    @property
    def create_lsl_outlet_daq(self) -> StreamOutlet:
        """Returns an LSL StreamOutlet for DAQ data

        Returns:
            StreamOutlet: The created LSL StreamOutlet object
        """        
        info = StreamInfo(name=self._name,
                        type='custom_daq',
                        channel_count=17, # 8 Data Channels +8 Error Flags(for each channel one)+ 1 Timestamp Channel 
                        nominal_srate=self._sampling_rate,
                        channel_format=cf_int32,
                        source_id=self._name + '_uid')
        return StreamOutlet(info)