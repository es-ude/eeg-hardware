#include "callbacks/rpc_callbacks.h"
#include "hardware_io.h"
#include "src/shielding_inputs.h"


// ============================= COMMANDS =============================
typedef enum {
    ECHO,
    RESET,
    CLOCK_SYS,
    STATE_SYS,
    STATE_PIN,
    RUNTIME,
    FIRMWARE,
    ENABLE_LED,
    DISABLE_LED,
    PING_LED,
    ERROR_STATUS_REG,
    START_DAQ,
    STOP_DAQ,
    UPDATE_DAQ,
    SET_PGA_GAIN,
    SET_CHANNELS,
    SET_SDO_STH,
    SET_SAMP_RATE,
    SET_TEST_MODE,
    SET_POWER_MODE,
    SET_HEADER_TYPE,
    SHIELDING_REF,
    POTI_SET_VALUE
} usb_cmd_t;


// ========================== PROCOTOL FUNCS ==========================
void echo(char* buffer, size_t length){
    usb_send_bytes(buffer, length);
}


void system_reset(void){
    reset_pico_mcu(true);
}


void get_state_system(char* buffer, size_t length){
    buffer[2] = system_state;
    usb_send_bytes(buffer, length);
}


void get_clock_system(char* buffer, size_t length){
    uint16_t clk_val = (uint16_t)(clock_get_hz(clk_sys) / 10000);
    buffer[1] = (uint8_t)(clk_val >> 0);
    buffer[2] = (uint8_t)(clk_val >> 8);
    usb_send_bytes(buffer, length);
}


void get_state_pin(char* buffer, size_t length){
    buffer[2] = gpio_get(SWITCH_SHIELDING_PIN_REF);
    usb_send_bytes(buffer, length);
}


void get_runtime(char* buffer){
    char buffer_send[9] = {0};
    buffer_send[0] = buffer[0];
    uint64_t runtime = get_runtime_ms();
    for(uint8_t idx = 0; idx < 8; idx++){
        buffer_send[idx+1] = (uint8_t)runtime;
        runtime >>= 8;
    }
    usb_send_bytes(buffer_send, sizeof(buffer_send));
}

void get_firmware_version(char* buffer, size_t length){
    buffer[1] = (char)FIRMWARE_VERSION_MAJOR;
    buffer[2] = (char)FIRMWARE_VERSION_MINOR;
    usb_send_bytes(buffer, length);
}


void enable_led(void){
    led_on(&led_1);
    led_on(&led_2);
}


void disable_led(void){
    led_off(&led_1);
    led_off(&led_2);
}


void ping_led(void){
    toggle_led(&led_1);
    toggle_led(&led_2);
}

void read_error_status_registers(void){
    uint8_t error_status_packet [17+2]; // 2 bytes for Header and endbyte
    error_status_packet[0] = 0xAA;
    error_status_packet[18] = 0xBB;
    ad7779_output_all_status_error_register(&ad, error_status_packet);
    usb_send_bytes((char*)error_status_packet, sizeof(error_status_packet));
}

void start_daq(void){
    if (! ad.data_read_mode) {
        ad7779_data_read_mode(&ad);
    }
    set_system_state(STATE_DAQ);
    //start_daq_sampling(&tmr_daq0_hndl);
}


void stop_daq(void){
    set_system_state(STATE_IDLE);
    if (ad.data_read_mode) {
        ad7779_data_read_mode(&ad);
    }
    //stop_daq_sampling(&tmr_daq0_hndl);
}


void update_daq(char* buffer){
    if (ad.data_read_mode) {
        ad7779_data_read_mode(&ad);
    }
    write_register_daq(&ad);
}


void set_pga_gain(char* buffer){
    uint8_t new_pga_gain = buffer[2];
    ad.pga_gain = new_pga_gain;
}


void set_channels(char* buffer){
    uint8_t new_channel_select = buffer[2];
    ad.channel_select = new_channel_select;
}

void set_sdo_strength(char* buffer){
    uint8_t new_sdo_strength = buffer[2];
    ad.sdo_driver_strength = new_sdo_strength;
}


void set_sampling_rate(char* buffer){
    uint16_t new_sampling_rate_hz = (buffer[1] << 8) | (buffer[2] << 0);
    ad.sampling_rate_SPS = new_sampling_rate_hz;
}


void set_test_mode(char* buffer){
    bool new_test_mode = buffer[2];
    ad.test_mode = new_test_mode;
}


void set_power_mode(char* buffer){
    bool new_power_mode = buffer[2];
    ad.high_power_mode = new_power_mode;
}


void set_header_type(char* buffer){
    bool new_header_type = buffer[2];
    ad.error_header = new_header_type;
}


void set_shielding_reference(char* buffer){
    bool new_shielding_reference = buffer[2];
    ad7779_enable_disable_shielding_electrode_ref(new_shielding_reference);
}


void set_poti_value(char* buffer){
    uint8_t new_poti_value = buffer[2];

    for (uint8_t i = 0; i < sizeof(poti)/sizeof(poti[0]); i++) {
        ad5142a_define_level(&poti[i], 0, new_poti_value);
        ad5142a_define_level(&poti[i], 1, new_poti_value);
    }
}


// ======================== CALLABLE FUNCS ==========================
bool apply_rpc_callback(char* buffer, size_t length, bool ready){    
    if(ready){
        switch(buffer[0]){
            case ECHO:              echo(buffer, length);                   break;
            case RESET:             system_reset();                         break;
            case CLOCK_SYS:         get_clock_system(buffer, length);       break;
            case STATE_SYS:         get_state_system(buffer, length);       break;
            case STATE_PIN:         get_state_pin(buffer, length);          break; 
            case RUNTIME:           get_runtime(buffer);                    break;
            case FIRMWARE:          get_firmware_version(buffer, length);   break;
            case ENABLE_LED:        enable_led();                           break;
            case DISABLE_LED:       disable_led();                          break;
            case PING_LED:          ping_led();                             break;
            case ERROR_STATUS_REG:  read_error_status_registers();          break;
            case START_DAQ:         start_daq();                            break;
            case STOP_DAQ:          stop_daq();                             break;
            case UPDATE_DAQ:        update_daq(buffer);                     break;
            case SET_PGA_GAIN:      set_pga_gain(buffer);                   break;
            case SET_CHANNELS:      set_channels(buffer);                   break;
            case SET_SDO_STH:       set_sdo_strength(buffer);               break;
            case SET_SAMP_RATE:     set_sampling_rate(buffer);              break;
            case SET_TEST_MODE:     set_test_mode(buffer);                  break;
            case SET_POWER_MODE:    set_power_mode(buffer);                 break;
            case SET_HEADER_TYPE:   set_header_type(buffer);                break;
            case SHIELDING_REF:     set_shielding_reference(buffer);        break;
            case POTI_SET_VALUE:    set_poti_value(buffer);                 break;
            default:                sleep_us(10);                           break;        
        }  
    }
    return true;
}
      