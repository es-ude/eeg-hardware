import serial
from serial.tools import list_ports
import time

#vid and pid for Pico
USB_VID = 0x2E8A
USB_PID = 0x0009


class SerialHandler:
    _com_name: str
    _baudrate: int
    _time_out: float
    _serial_connection: serial.Serial
    """Class to handle serial communication with EEG hardware devices"""
    def __init__(self, com_name: str ="AUTOCOM", baudrate: int = 115200, time_out: float = 1.0):
        self._com_name = com_name if com_name != "AUTOCOM" else self._scan_com_name[0]
        self._baudrate = baudrate
        self._time_out = time_out
        self._serial_connection = self._init_serial_connection


    @property
    def get_serial_connection(self) -> serial.Serial:
        """Get the initialized serial connection

        Returns:
            serial.Serial: The initialized serial connection object
        """
        return self._serial_connection
    

    @property
    def __read_usb_properties(self) -> list:
        """Reading the USB properties of all devices device

        Returns:
            list: List of dictionaries with COM port, PID, and VID information
        """
        return [{"com": ps.device, "pid": ps.pid, "vid": ps.vid} for ps in list_ports.comports()]


    @property
    def _scan_com_name(self) -> list:
        """Returning the COM Port name of the addressable devices

        Raises:
            ConnectionError: If no COM ports with the specified VID and PID are found

        Returns:
            list: List of COM port names matching the specified VID and PID
        """
        available_coms = list_ports.comports()
        list_right_com = [port.device for port in available_coms if
                          port.vid == USB_VID and port.pid == USB_PID]
        if len(list_right_com) == 0:
            raise ConnectionError(f"No COM Port with right USB found - Please adapt the VID and PID values from "
                                  f"available COM ports: {self.__read_usb_properties}")
        #self.__logger.debug(f"Found {len(list_right_com)} COM ports available")
        return list_right_com


    @property
    def _init_serial_connection(self) -> serial.Serial:
        """Initialize serial connection

        Raises:
            IOError: If there is an error initializing the serial connection

        Returns:
            serial.Serial: Initialized serial connection object
        """
        try: 
            deployed_serial = serial.Serial(
                port=self._com_name,
                baudrate=self._baudrate,
                inter_byte_timeout=1,
                bytesize=serial.EIGHTBITS, 
                parity=serial.PARITY_NONE, 
                stopbits=serial.STOPBITS_ONE, 
                xonxoff=False,
                rtscts=False,
                dsrdtr=False,
                timeout=self._time_out
            )
            time.sleep(2*self._time_out)
        except serial.SerialException as e:
            raise IOError(f"Error initializing serial connection: {e}")
        return deployed_serial
    

    def clear_serial_buffer(self) -> None:
        """Clear the serial input buffer to remove any residual data"""
        self._serial_connection.reset_input_buffer()    