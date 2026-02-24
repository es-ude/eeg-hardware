#ifndef DAQ_SAMPLE_H_
#define DAQ_SAMPLE_H_


#include "hal/tmr/tmr.h"
#include "adc/ad7779/ad7779.h"


/*! \brief Data structure for DAQ sampling data packet
* \param packet_id  Identifier for the data packet type
* \param iteration  Iteration count of the sampling
* \param runtime    Actual runtime in microseconds since system start
* \param channel_id Identifier for the data channel
* \param value      Sampled data value
*/
typedef struct {
    uint8_t packet_id;
    uint8_t iteration;
    uint64_t runtime;
    uint8_t channel_id;
    uint16_t value;
} daq_data_t;


/*! \brief Function to write configuration registers to the DAQ unit
* \param handler    Pointer to typedef struct ad7779_t to handle the settings
* \return           true if write was successful, false otherwise
*/
bool write_register_daq(ad7779_t* handler);


/*! \brief Function to start the DAQ sampling unit
* \param handler        Pointer to the timer IRQ handler structure
* \return               State of the DAQ sampling unit (true=running, false=deactivated)
*/
bool start_daq_sampling(tmr_repeat_irq_t* handler);


/*! \brief Function to stop the DAQ sampling unit
* \param handler        Pointer to the timer IRQ handler structure
* \return               State of the DAQ sampling unit (true=deactivated, false=activated)
*/
bool stop_daq_sampling(tmr_repeat_irq_t* handler);
#endif