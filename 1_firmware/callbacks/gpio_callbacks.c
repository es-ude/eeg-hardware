#include "callbacks/gpio_callbacks.h"
#include "hardware_io.h"


// ============================== ISR ROUTINES ==============================
void irq_gpio_button_user(uint gpio, uint32_t events, uint8_t gpio_led){
    gpio_put(gpio_led, !gpio_get(gpio_led));
}

void isr_gpio_data_ready(uint gpio, uint32_t events) {
    packet.timestamp = get_runtime_ms();
    data_ready_flag = true;
}


void irq_gpio_callbacks(uint gpio, uint32_t events){
    switch(gpio){
        //case BUTTON_BOARD:  irq_gpio_button_user(gpio, events, LED_TEST_DEFAULT);   break;
		case ADC_DATA_READY_PIN: isr_gpio_data_ready(gpio, events); break;
        default:			sleep_us(1);											break;
    };
}
