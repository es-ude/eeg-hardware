import unittest
from .poti import calculate_poti_value, calculate_requierd_resistor_value_for_amplification

class TestPoti(unittest.TestCase):
    def test_calculate_requierd_resistor_value_for_amplification_gain_in_range(self):
        gain = 2
        expected_resistor_value = 19.8e3/(gain-1)

        actual_resistor_value = calculate_requierd_resistor_value_for_amplification(gain)
        self.assertAlmostEqual(expected_resistor_value, actual_resistor_value)


    def test_calculate_requierd_resistor_value_for_amplification_gain_exactly_one(self):
        gain = 1
        expected_resistor_value = 100e3

        actual_resistor_value = calculate_requierd_resistor_value_for_amplification(gain)
        self.assertEqual(expected_resistor_value, actual_resistor_value)

    
    def test_calculate_requierd_resistor_value_for_amplification_gain_too_high(self):
        gain = 1000
        expected_resistor_value = 130

        actual_resistor_value = calculate_requierd_resistor_value_for_amplification(gain)
        self.assertEqual(expected_resistor_value, actual_resistor_value)


    def test_gain_smaller_than_one_raises_value_error(self):
        gain = 0.5
        
        with self.assertRaises(ValueError):
            calculate_requierd_resistor_value_for_amplification(gain)


    def test_calculate_poti_value(self):
        resistor_value = 1000
        expected_poti_value = int(255 - ((resistor_value-130) / 391))

        results = calculate_poti_value(resistor_value)
        self.assertEqual(expected_poti_value, results[0])