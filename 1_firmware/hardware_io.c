#include "hardware_io.h"


system_state_t system_state = STATE_ERROR;
// ==================== I2C DEFINITION =====================
i2c_rp2_t my_i2c = {
	.pin_sda = I2C_SDA_PIN,
	.pin_scl = I2C_SCL_PIN,
	.i2c_mod = i2c1,
	.fi2c_khz = 100,
	.avai_devices = 0, 
	.init_done = false
};


// ==================== SPI DEFINITION =====================
spi_rp2_t my_spi = {
    .pin_mosi = PICO_DEFAULT_SPI_TX_PIN,
    .pin_sclk = PICO_DEFAULT_SPI_SCK_PIN,
    .pin_miso = PICO_DEFAULT_SPI_RX_PIN,
    .spi_mod = spi0,
    .fspi_khz = 2000,            // z. B. 10 MHz
    .mode = 0,                   // SPI Mode 0
    .msb_first = true,     
    .init_done = false
};


// ==================== PICO/SYSTEM DEFINITION =====================
// --- USB PROTOCOL
char data_usb[USB_FIFO_SIZE] = {0};
usb_rp2_t usb_buffer = {
	.ready = false,
	.length = USB_FIFO_SIZE,
	.position = USB_FIFO_SIZE-1,
	.data = data_usb
};  

// --- LED Handling
led_t led_1 = {
	.pin = LED_01_PIN,
	.state = false,
	.init_done = false
};
led_t led_2 = {
	.pin = LED_02_PIN,
	.state = false,
	.init_done = false
};


// --- Poti Handling AD5142A
uint8_t poti_adr[4] = {0, 2, 6, 8};
ad5142a_t poti[4] = {
	{
		.i2c_handler = &my_i2c,
		.adr = 0x00,
		.init_done = false
	},
	{
		.i2c_handler = &my_i2c,
		.adr = 0x00,
		.init_done = false
	},
	{
		.i2c_handler = &my_i2c,
		.adr = 0x00,
		.init_done = false
	},
	{
		.i2c_handler = &my_i2c,
		.adr = 0x00,
		.init_done = false
	}
};

// --- DAQ Handling AD7779
// Setup AD7779 GPIO handler
ad7779_gpio_t ad_gpio = {
	.cs_pin = SPI_ADC_CS_PIN,
	.reset_pin = ADC_RESET_PIN,
	.start_pin = ADC_START_PIN,
	.init_done = false
};

// Setup AD7779 handler
ad7779_t ad = { // definition of the AD7779 handler
	.spi = &my_spi,
	.gpio = &ad_gpio,
	.pga_gain = 1, // PGA Gain setting (1, 2, 4, 8)
	.channel_select = 0xFF, // Enable all channels
    .sdo_driver_strength =0, // Extra Strong SDO Driver Strength
    .sampling_rate_SPS = 2000, // Sampling Rate 2kSPS
	.test_mode = false, // Disable Test Mode
	.high_power_mode = true, // Enable High Power Mode
	.error_header = false, // Disable Error Header
    .data_read_mode = false,
	.init_done = false
};