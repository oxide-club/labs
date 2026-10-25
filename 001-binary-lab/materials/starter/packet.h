/* SPDX-License-Identifier: MIT */
#ifndef OXIDE_PACKET_H
#define OXIDE_PACKET_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    uint32_t version;
    uint32_t type;
    uint32_t flags;
    uint32_t length;
} Header;

bool header_pack(const Header *in, uint32_t *out);
void header_unpack(uint32_t word, Header *out);
void store_le32(uint8_t out[4], uint32_t word);
uint32_t load_le32(const uint8_t in[4]);

#endif
