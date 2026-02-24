#include "adc_data_processing.h"

bool extract_headers_from_adc_data(uint8_t *complete_adc_data_packet, uint8_t *raw_channel_data) {    
    int dest_index = 0;
    for (int i = 0; i < 32; i++) {
        if (i %4 ==0) { // Skip header bytes
            continue;
        }
        raw_channel_data[dest_index] = complete_adc_data_packet[i];   // Extract the 24-bit ADC value
        dest_index++;
    }
    return true;
}

bool extract_alert_bytes_from_adc_data(uint8_t *complete_adc_data_packet, uint8_t *alert_byte) {    
    // Each alert byte is the first byte of each 4-byte channel data
    *alert_byte = 0;
    for (int i = 0; i < 32; i = i+4) {
        uint8_t bit = (complete_adc_data_packet[i]>>7) &1; //with >>7 the last bit is shifted to the first position e.g 7 steps; with &1 (bit mask) only the last bit is kept
        *alert_byte |= bit << (7 - (i/4)); // Set the corresponding bit in the alert_byte
    }
    return true;
}