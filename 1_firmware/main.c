#include "hardware_io.h"
#include "callbacks/rpc_callbacks.h"
#include "src/adc_data_processing.h"



// ========================= DEFINITIONS =========================
volatile bool data_ready_flag = false; // Flag to indicate if data is ready for reading from the ADC
volatile bool data_ready_for_processing = false; // Flag to indicate if data is ready for processing
volatile bool data_ready_for_sending = false; // Flag to indicate data is ready for sending
adcDataPacket_t packet;

int main(){   
    // Init Phase
    init_gpio_pico(false);
    init_system();
    sleep_ms(10);

    // - - - - Main Loop - - - -
    uint8_t packages_sent_counter = 0;
    uint8_t raw_return_data[32];
    while (true) {
        if (get_system_state() == STATE_DAQ) {
            if (data_ready_flag) {
                data_ready_flag = false;
                ad7779_read_all_channel_data(&ad, raw_return_data);
                data_ready_for_processing = true; // Set flag to process data
            }
            if (data_ready_for_processing) {
                data_ready_for_processing = false;    
                extract_headers_from_adc_data(raw_return_data, packet.extracted_data);
                extract_alert_bytes_from_adc_data(raw_return_data, &packet.alert_byte);
                data_ready_for_sending = true; // Set flag to send data
            }
            if (data_ready_for_sending) {
                data_ready_for_sending = false;
                send_all_channel_data_binary(&packet, &ad.channel_select, &packages_sent_counter);
            }
        }
        usb_handling_fifo_buffer(&usb_buffer);
        apply_rpc_callback(*usb_buffer.data, usb_buffer.length, usb_buffer.ready);
    };
}
