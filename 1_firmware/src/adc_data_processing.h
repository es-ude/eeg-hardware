#ifndef ADC_DATA_PROCESSING_H
#define ADC_DATA_PROCESSING_H
#include <stdint.h>
#include <stdbool.h>

bool extract_headers_from_adc_data(uint8_t *complete_adc_data_packet, uint8_t *raw_channel_data);
bool extract_alert_bytes_from_adc_data(uint8_t *complete_adc_data_packet, uint8_t *alert_byte);



#endif