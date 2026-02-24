#ifndef SHIELDING_INPUTS_H
#define SHIELDING_INPUTS_H

#include "hardware_io.h"

/**
 * \brief Enable/disable active shielding for electrode reference
 * \param shielding_active   true to enable shielding, false to disable
 * \return           true if trigger was successful, false otherwise.
 */
bool ad7779_enable_disable_shielding_electrode_ref(bool shielding_active);

#endif