#ifndef LED_HANDLER_H_
#define LED_HANDLER_H_


#include "pico/stdlib.h"
#include <stdint.h>

/*! \brief Structure to setup the GPIO pins for the AD7779
    \param pin          GPIO pin number for the LED
    \param state        Boolean to hold the current state of the LED (on/off)
    \param init_done    Flag to indicate if initialization was successful
*/
typedef struct {
    uint8_t pin;
    bool state;
    bool init_done;
} led_t;


/*! \brief function to initialize a GPIO pin for an LED: sets the pin as an output and turns it off
    \param handler      Handler struct for the LED to be initialized, the pin number must be set before calling this function
*/
bool init_led(led_t *handler);


/*! \brief Function to turn on an LED
    \param handler      Handler struct for the LED to be initialized, the pin number must be set before calling this function
*/
bool led_on(led_t *handler);


/*! \brief Function to turn off an LED
    \param handler      Handler struct for the LED to be initialized, the pin number must be set before calling this function
*/
bool led_off(led_t *handler);


/*! \brief Function to toggle an LED
    \param handler      Handler struct for the LED to be toggled, the pin number must be set before calling this function
*/
bool toggle_led(led_t *handler);
#endif
