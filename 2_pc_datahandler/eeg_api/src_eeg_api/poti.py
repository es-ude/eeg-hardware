import warnings
from dataclasses import dataclass

@dataclass
class PotiConfig:
    """Data class to store the potentiometer configuration for a given gain of the instrumentation amplifier
    Attributes:
        gain (int): Gain of the instrumentation amplifier
        calculated_resistor_value (float): Calculated resistor value for the given gain of the instrumentation amplifier
        poti_value (int): Potentiometer value to be set on the device for the desired gain of the instrumentation amplifier (0-255)
        actual_resistor_value (float): Actual resistor value based on the potentiometer characteristics
        actual_gain_value (float): Actual gain value based on the actual resistor value
    """    
    gain: int
    calculated_resistor_value: float
    poti_value: int
    actual_resistor_value: float
    actual_gain_value: float


def generate_poti_config(gain: int) -> PotiConfig:
    """Generates a PotiConfig dataclass for a given gain of the instrumentation amplifier
        gain (int): Gain of the instrumentation amplifier

    Returns:
        PotiConfig: PotiConfig dataclass with gain, calculated resistor value, poti value and actual resistor value
    """    
    return PotiConfig(
        gain=gain,
        calculated_resistor_value=None,
        poti_value=None,
        actual_resistor_value=None,
        actual_gain_value=None
    )


def calculate_requierd_resistor_value_for_amplification(gain: int,  min_resistor_value: float = 130, max_resistor_value: float = 100e3) -> float:
    """Calculates the required resistor value for a given gain of the amplifier

    Args:
        gain (int): Gain of the amplifier
        min_resistor_value (float, optional): Minimum resistor value in Ohm. Defaults to 130 (defalut value is based on the datasheet from the Poti)
        max_resistor_value (float, optional): Maximum resistor value in Ohm. Defaults to 100e3 (defalut value is based on the datasheet from the Poti)
        
    Raises:
        ValueError: If gain is smaller than 1

    Returns:
        float: Required poti resistor value in Ohm
    """
    if gain < 1:
        raise ValueError("Gain must be greater 1")
    if gain == 1:
        poti_resistor_value = max_resistor_value
    else: 
        poti_resistor_value = 19.8e3/(gain-1)
    
    if poti_resistor_value > max_resistor_value:
        warnings.warn(f"Poti resistor value is greater than {max_resistor_value}Ohm, value is set to {max_resistor_value}Ohm")
        poti_resistor_value = max_resistor_value
    elif poti_resistor_value < min_resistor_value:
        warnings.warn(f"Poti resistor value is smaller than {min_resistor_value}Ohm, value is set to {min_resistor_value}Ohm")
        poti_resistor_value = min_resistor_value
    return poti_resistor_value


def calculate_poti_value(resistor_value: int, wiper_resistor_value: int = 130):
    """Calculates the poti value and actual resistor value for a given resistor value

    Args:
        resistor_value (int): Resistor value in Ohm
        wiper_resistor_value (int, optional): Wiper resistor value in Ohm. Defaults to 130. (defalut value is based on the datasheet from the Poti)

    Returns:
        tuple[int, float]: Tuple with poti value and actual resistor value in Ohm
    """    
    poti_value = int(255 - ((resistor_value-wiper_resistor_value) / 391))
    actual_resistor_value = poti_value * 393 + wiper_resistor_value
    return poti_value, actual_resistor_value


def calculate_gain(resistor_value: float) -> float:
    """Calculates the gain of the amplifier for a given resistor value

    Args:
        resistor_value (int): Resistor value in Ohm

    Returns:
        float: Gain of the amplifier
    """
    gain = 1 + (19.8e3 / resistor_value)
    return gain
