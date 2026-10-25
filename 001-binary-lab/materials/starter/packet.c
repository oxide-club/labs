/* SPDX-License-Identifier: MIT */
#include "packet.h"

/* Starter incompleto: substitua os corpos conforme o contrato. */
bool header_pack(const Header *in, uint32_t *out) {
    (void)in;
    (void)out;
    return false;
}

void header_unpack(uint32_t word, Header *out) {
    (void)word;
    (void)out;
}

void store_le32(uint8_t out[4], uint32_t word) {
    (void)out;
    (void)word;
}

uint32_t load_le32(const uint8_t in[4]) {
    (void)in;
    return 0;
}
