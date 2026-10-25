/* SPDX-License-Identifier: MIT */
#include <inttypes.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

struct A { uint8_t tag; uint32_t length; uint16_t flags; };
struct B { uint32_t length; uint16_t flags; uint8_t tag; };

static void store(uint8_t out[4], uint32_t word, int big) {
    for (unsigned i = 0; i < 4; ++i)
        out[i] = (uint8_t)(word >> (8 * (big ? 3 - i : i)));
}

static uint32_t load_be(const uint8_t in[4]) {
    return ((uint32_t)in[0] << 24) | ((uint32_t)in[1] << 16)
         | ((uint32_t)in[2] << 8) | (uint32_t)in[3];
}

static void bytes(const unsigned char *p, size_t n) {
    for (size_t i = 0; i < n; ++i)
        printf("%s%02X", i ? " " : "", (unsigned)p[i]);
}

/* Formato externo de sete bytes: tag, length LE32, flags LE16. */
static void record(uint8_t out[7], uint8_t tag, uint32_t length, uint16_t flags) {
    out[0] = tag;
    store(out + 1, length, 0);
    out[5] = (uint8_t)flags;
    out[6] = (uint8_t)(flags >> 8);
}

int main(void) {
    const uint32_t words[] = {UINT32_C(0x01020304), UINT32_C(0x22500102), UINT32_MAX};
    for (size_t i = 0; i < sizeof words / sizeof words[0]; ++i) {
        uint8_t le[4], be[4];
        store(le, words[i], 0);
        store(be, words[i], 1);
        printf("word=0x%08" PRIX32 " host=", words[i]);
        bytes((const unsigned char *)&words[i], sizeof words[i]);
        printf(" LE="); bytes(le, 4);
        printf(" BE="); bytes(be, 4);
        printf(" wrong=0x%08" PRIX32 "\n", load_be(le));
    }
    const struct A a = {.tag = 7, .length = UINT32_C(0x01020304), .flags = UINT16_C(0x0506)};
    const struct B b = {.length = UINT32_C(0x01020304), .flags = UINT16_C(0x0506), .tag = 7};
    uint8_t external_a[7], external_b[7];
    record(external_a, a.tag, a.length, a.flags);
    record(external_b, b.tag, b.length, b.flags);
    printf("A size=%zu align=%zu tag=%zu length=%zu flags=%zu\n",
           sizeof a, _Alignof(struct A), offsetof(struct A, tag),
           offsetof(struct A, length), offsetof(struct A, flags));
    printf("B size=%zu align=%zu tag=%zu length=%zu flags=%zu\n",
           sizeof b, _Alignof(struct B), offsetof(struct B, tag),
           offsetof(struct B, length), offsetof(struct B, flags));
    printf("logical_equal=%d external_equal=%d external=",
           a.tag == b.tag && a.length == b.length && a.flags == b.flags,
           memcmp(external_a, external_b, 7) == 0);
    bytes(external_a, 7); putchar('\n');
    /* Não lemos bytes de padding nem os usamos como critério de igualdade. */
    return 0;
}
