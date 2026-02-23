#include "shielding_inputs.h"

bool ad7779_enable_disable_shielding_electrode_ref(bool shielding_active){
    gpio_put(SWITCH_SHIELDING_PIN_REF, shielding_active); // Enable shielding electrode reference
    return true;
}