#include "src/init_system.h"
#ifdef PICO_CYW43_SUPPORTED
    #include "pico/cyw43_arch.h"
#endif
#include "hardware_io.h"
#include "hardware/watchdog.h"
#include "callbacks/gpio_callbacks.h"


void reset_pico_mcu(bool wait_until_done){
    set_system_state(STATE_RESET);
    watchdog_enable(100, 1);
    if(wait_until_done){
        while(true){
            tight_loop_contents();
        }
    };
}


bool init_gpio_pico(bool block_usb){
    set_system_state(STATE_INIT);
    // --- Init of Wireless Module (if used)
    #ifdef PICO_CYW43_SUPPORTED 
        if (cyw43_arch_init()) {
            return false;
        }
    #endif
    
    // --- Init of GPIOs
    init_led(&led_1);
    init_led(&led_2);


    // --- Init Data Ready Pin with IRQ
    gpio_init(ADC_DATA_READY_PIN);
    gpio_set_dir(ADC_DATA_READY_PIN, GPIO_IN);
    gpio_set_irq_enabled_with_callback(ADC_DATA_READY_PIN, GPIO_IRQ_EDGE_FALL, true, &irq_gpio_callbacks);
    irq_set_priority(IO_IRQ_BANK0, 0);


    // --- Init DRDY Pin
    gpio_init(ADC_DATA_READY_PIN);
    gpio_set_dir(ADC_DATA_READY_PIN, GPIO_IN);


    // --- Init and switch on Power of the PCB
    gpio_init(EN_POWER_PIN);
    gpio_set_dir(EN_POWER_PIN, GPIO_OUT);
    gpio_put(EN_POWER_PIN, 1); // power on


    // --- Init and switch off Schielding for Electrode Reference
    gpio_init(SWITCH_SHIELDING_PIN_REF);
    gpio_set_dir(SWITCH_SHIELDING_PIN_REF, GPIO_OUT);
    gpio_put(SWITCH_SHIELDING_PIN_REF, 0); // shielding to G


    // --- Init of Serial COM-Port
    usb_init();
    if(block_usb){
        usb_wait_until_connected();
    }
    return true;
}


bool init_pio_adc_clk() {
    PIO pio = pio0;
    if (ad.high_power_mode) {
        clk_generation_pio_init(pio, ADC_MCLK_PIN, ADC_TARGET_FREQ_HIGH_POWER);
    } else {
        clk_generation_pio_init(pio, ADC_MCLK_PIN, ADC_TARGET_FREQ_LOW_POWER);
    }
    return true;
}


bool init_potis(){
    bool init_done = true;
    for(uint8_t i = 0; i < sizeof(poti)/sizeof(poti[0]); i++){
        if(!ad5142a_init(&poti[i], poti_adr[i])){
            init_done = false;
        }
        if(!ad5142a_define_level(&poti[i], 0, 255)){ //Set default poti value to the lowest Resitor value
            init_done = false;
        }
        if (!ad5142a_define_level(&poti[i], 1, 255)){
            init_done = false;
        }
    }
    return init_done;
}


bool init_system(void){
    uint8_t num_init_done = 0;
    if (init_pio_adc_clk()){
        num_init_done++;
    }
    
    if (init_potis()){
        num_init_done++;
    }

    if (ad7779_init(&ad)){
        num_init_done++;
    }

    // --- Blocking Routine if init is not completed
    sleep_ms(10);
    if(num_init_done == 3){
        set_system_state(STATE_IDLE);
        return true;
    } else {
        set_system_state(STATE_ERROR);
        return false;
    }
}


uint64_t get_runtime_ms(void){
    absolute_time_t now = get_absolute_time();
    return to_us_since_boot(now);
}


system_state_t get_system_state(void){
    return system_state;
}


bool set_system_state(system_state_t new_state){
    bool valid_state = false;
    
    if((system_state != new_state)){
        system_state = new_state;
        switch(new_state){
            case STATE_INIT:
                led_on(&led_2);
                led_off(&led_1);
                valid_state = true;
                break;
            case STATE_IDLE:
                led_on(&led_2);
                led_off(&led_1);
                valid_state = true;
                break;
            case STATE_ERROR:
                led_on(&led_1);
                led_off(&led_2);
                valid_state = false;
                break;
            case STATE_DAQ:
                led_on(&led_1);
                led_on(&led_2);
                valid_state = true;
                break;
            default:
                valid_state = false;
                break;
        }
        return valid_state;
    } else {
        return false;
    };    
}
