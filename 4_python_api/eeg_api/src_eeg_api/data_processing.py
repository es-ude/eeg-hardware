import numpy as np

def extract_channel_data(raw_data_packet: np.ndarray) -> list:
    """

    Args:
        raw_data_packet (np.ndarray): The raw data packet containing the channel data

    Returns:
        list: List of extracted channel data points
    """
    data_points = []
    for position_first_byte in range (0, len(raw_data_packet), 3):
        channel_value = int.from_bytes(raw_data_packet[position_first_byte:position_first_byte+3], byteorder='big', signed=True)
        data_points.append(channel_value)
    return data_points


def extract_error_flags(error_flag_byte: int) -> list:
    """Extracts the error flags from the given byte and returns them as a list of integers (0 or 1)

    Args:
        error_flag_byte (int): The error flag byte to extract flags from

    Returns:
        list: List of error flags (0 or 1) for each channel
    """    
    channel_flags = []
    for bit_position in range(8):
        if (error_flag_byte >> bit_position) & 0x01:
            channel_flags.append(1)
        else:
            channel_flags.append(0)
    return channel_flags