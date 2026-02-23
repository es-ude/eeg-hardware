#ifndef PACKET_FRAMES_H
#define PACKET_FRAMES_H

#include "pico/stdlib.h"
#include <stdio.h>

// --- Definition of Paket IDS
#define RAW_DATA_PACKET_ID 0x00

/**
 * \brief Data Packet Structure for ADC Data Transmission
 * \param header            Header byte (0xAA)
 * \param frame_id          Constants defining the type of data packet
 * \param packet_number     Sequential packet number
 * \param timestamp         Timestamp in microseconds since boot
 * \param active_channels   Bitmask representing active channels
 * \param alert_byte        Alert byte indicating any alerts
 * \param extracted_data    Extracted ADC data bytes
 * \param stop              Stop byte (0xBB)
 */
typedef struct __attribute__((packed)) {
    uint8_t header;          // 0xAA
    uint8_t frame_id;
    uint8_t packet_number;
    uint64_t timestamp;
    uint8_t active_channels;
    uint8_t alert_byte;
    uint8_t extracted_data[24];    // 8 Channels * 3 Bytes
    uint8_t stop;            // 0xBB
} adcDataPacket_t;


void send_all_channel_data_binary(adcDataPacket_t *packet, uint8_t *channel_select, uint8_t *package_sent_counter);
#endif