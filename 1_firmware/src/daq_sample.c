#include "src/daq_sample.h"
#include "sens/ad7779.h"
#include "hal/usb/usb.h"


//==================== CALLABLE FUNCS ====================//
bool write_register_daq(ad7779_t *handler){
    int8_t init = 0; 
    
    if (ad7779_set_spi_sync(handler)) { //safe
        init++;}

    if (default_state_mux_register(handler)) { //safe
        init++;}   

    if (ad7779_set_sdo_driver_strength(handler)) {
        init++;}

    if (ad7779_set_power_mode(handler)) {
        init++;}

    if (ad7779_set_sampling_rate(handler)) {
        init++;}

    if (ad7779_enable_disable_channels(handler)) { //safe
          init++;}

    if (ad7779_configure_pga_for_all_channels(handler)) { //safe
        init++;}

    if (ad7779_switch_daq_header(handler)) { //safe
        init++;}
    
    if (ad7779_enable_disable_test_mode(handler)) {
        init++;}

    if (ad7779_start_pin(handler)) {
        init++;}

    sleep_ms(10); // wait for settings to take effect
    
    if (init == 10){
        return true;
    } else {
        return false;
    }
};


bool start_daq_sampling(tmr_repeat_irq_t* handler){
    return enable_repeat_timer_irq(handler);
};


bool stop_daq_sampling(tmr_repeat_irq_t* handler){
    return disable_repeat_timer_irq(handler);
};