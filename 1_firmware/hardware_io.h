#ifndef HARDWARE_IO_H_
#define HARDWARE_IO_H_


#include "hardware/gpio.h"
#include "hardware/clocks.h"
#include "hal/tmr/tmr.h"
#include "hal/usb/usb.h"
#include "hal/spi/spi.h"
#include "hal/clk/pio_clock.h"

#include "src/init_system.h"
#include "src/testbench.h"
#include "src/packet_frames.h"
#include "src/daq_sample.h"
#include "src/led_handler.h"

#include "poti/AD5142A/ad5142a.h"

#include "adc/ad7779/ad7779.h"

#define FIRMWARE_VERSION_MAJOR 2
#define FIRMWARE_VERSION_MINOR 1
extern system_state_t system_state;
// ==================== PIN DEFINITION =====================
#define LED_01_PIN                  0 //Red LED
#define LED_02_PIN                  1 //Green LED

#define SWITCH_SHIELDING_PIN_REF    28
#define ADC_MCLK_PIN                13
#define ADC_START_PIN               23
#define EN_POWER_PIN                6
#define ADC_RESET_PIN               11
#define SPI_ADC_CS_PIN              17
#define ADC_DATA_READY_PIN          14

#define I2C_SDA_PIN                 26
#define I2C_SCL_PIN                 27    

// ==================== I2C DEFINITION =====================
extern i2c_rp2_t my_i2c;


// ==================== SPI DEFINITION =====================
//extern spi_rp2_t spi_mod;
extern spi_rp2_t my_spi;


// ================ PICO/SYSTEM DEFINITION =================
// --- Definition of output Frequency for ADC MCLK
#define ADC_TARGET_FREQ_HIGH_POWER  8192000
#define ADC_TARGET_FREQ_LOW_POWER   4096000

// --- USB Communication
#define USB_FIFO_SIZE 3
extern char data[USB_FIFO_SIZE];
extern usb_rp2_t usb_buffer;

// --- DAQ Handling
extern adcDataPacket_t packet;
extern volatile bool data_ready_flag;
extern ad7779_t ad;

// --- Poti Handling
extern ad5142a_t poti[4];
extern uint8_t poti_adr [4];

// --- LED Handling
extern led_t led_1;
extern led_t led_2;
#endif
