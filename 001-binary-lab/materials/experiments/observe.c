/* SPDX-License-Identifier: MIT */
#include "packet.h"
#include <inttypes.h>
#include <stdio.h>

int main(void) {
    const uint32_t word = UINT32_C(0x22500102);
    const unsigned char *host = (const unsigned char *)&word;
    uint8_t external[4] = {0xa5, 0xa5, 0xa5, 0xa5};
    store_le32(external, word);
    printf("word: 0x%08" PRIX32 "\n", word);
    printf("host:");
    for (unsigned i = 0; i < sizeof word; ++i) printf(" %02X", (unsigned)host[i]);
    printf("\nexternal:");
    for (unsigned i = 0; i < 4; ++i) printf(" %02X", (unsigned)external[i]);
    printf("\nsizeof Header: %zu; sizeof word: %zu\n", sizeof(Header), sizeof word);
    return 0;
}
