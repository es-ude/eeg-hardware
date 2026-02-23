#include "src/led_handler.h"

bool init_led(led_t *handler) {
    gpio_init(handler->pin);
    gpio_set_dir(handler->pin, GPIO_OUT);
    gpio_put(handler->pin, 0);
    handler->state = false;
    handler->init_done = true;
    return true;
}


bool led_on(led_t *handler) {
    if (!handler->init_done) return false;
    if (handler->state) return true;
    else {
        gpio_put(handler->pin, 1);
        handler->state = true;
        return true;
    }
    return false;
}


bool led_off(led_t *handler) {
    if (!handler->init_done) return false;
    if (!handler->state) return true;
    else {
        gpio_put(handler->pin, 0);
        handler->state = false;
        return true;
    }
    return false;
}


bool toggle_led(led_t *handler) {
    if (!handler->init_done) return false;
    if (handler->state) {
        gpio_put(handler->pin, 0);
        handler->state = false;
    } else {
        gpio_put(handler->pin, 1);
        handler->state = true;
    }
    return true;
}