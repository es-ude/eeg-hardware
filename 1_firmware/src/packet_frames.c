#include "packet_frames.h"

void send_all_channel_data_binary(adcDataPacket_t *packet, uint8_t *channel_select, uint8_t *package_sent_counter) {
    packet->header = 0xAA;
    packet->frame_id = RAW_DATA_PACKET_ID;
    packet->packet_number = (*package_sent_counter)++;
    packet->active_channels = *channel_select;
    packet->stop = 0xBB;
    fwrite(packet, sizeof(*packet), 1, stdout);
    fflush(stdout);
}