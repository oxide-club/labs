/* SPDX-License-Identifier: MIT */
#include "packet.h"
#include <limits.h>
#include <stdio.h>
#include <string.h>

_Static_assert(CHAR_BIT == 8, "Este laboratorio requer bytes de oito bits");
static unsigned checks, failures;
#define CHECK(expr) do { ++checks; if (!(expr)) { \
    ++failures; if (failures <= 20) \
    fprintf(stderr, "FALHA linha %d: %s\n", __LINE__, #expr); \
} } while (0)

static void same_header(Header a, Header b) {
    CHECK(a.version == b.version);
    CHECK(a.type == b.type);
    CHECK(a.flags == b.flags);
    CHECK(a.length == b.length);
}

/* Constantes independentes: nao derivar bytes usando a API sob teste. */
static void known_vectors(void) {
    static const struct {
        Header fields;
        uint32_t word;
        uint8_t bytes[4];
    } vectors[] = {
        {{0, 0, 0, 0}, UINT32_C(0), {0, 0, 0, 0}},
        {{1, 2, 5, 258}, UINT32_C(0x22500102), {0x02, 0x01, 0x50, 0x22}},
        {{2, 17, 8, 4096}, UINT32_C(0x51801000), {0, 0x10, 0x80, 0x51}},
        {{7, 31, 15, 1048575}, UINT32_MAX, {0xff, 0xff, 0xff, 0xff}}
    };
    for (unsigned i = 0; i < sizeof vectors / sizeof vectors[0]; ++i) {
        uint32_t word = UINT32_C(0xA5A5A5A5);
        Header got = {99, 99, 99, 99};
        uint8_t guarded[6] = {0x9a, 0xa5, 0xa5, 0xa5, 0xa5, 0x6b};
        CHECK(header_pack(&vectors[i].fields, &word));
        CHECK(word == vectors[i].word);
        header_unpack(vectors[i].word, &got);
        same_header(got, vectors[i].fields);
        store_le32(guarded + 1, vectors[i].word);
        CHECK(memcmp(guarded + 1, vectors[i].bytes, 4) == 0);
        CHECK(guarded[0] == 0x9a && guarded[5] == 0x6b);
        CHECK(load_le32(vectors[i].bytes) == vectors[i].word);
    }
}

static void invalid_inputs(void) {
    static const Header bad[] = {
        {8, 2, 5, 258}, {1, 32, 5, 258}, {1, 2, 16, 258},
        {1, 2, 5, 1048576}, {UINT32_MAX, 0, 0, 0},
        {0, UINT32_MAX, 0, 0}, {0, 0, UINT32_MAX, 0},
        {0, 0, 0, UINT32_MAX}
    };
    for (unsigned i = 0; i < sizeof bad / sizeof bad[0]; ++i) {
        uint32_t word = UINT32_C(0xA5A5A5A5);
        Header before = bad[i], input = before;
        CHECK(!header_pack(&input, &word));
        CHECK(word == UINT32_C(0xA5A5A5A5));
        same_header(input, before);
    }
    Header valid = {1, 2, 5, 258};
    uint32_t word = UINT32_C(0xA5A5A5A5);
    CHECK(!header_pack(NULL, &word));
    CHECK(word == UINT32_C(0xA5A5A5A5));
    CHECK(!header_pack(&valid, NULL));
    CHECK(!header_pack(NULL, NULL));
    /* As outras tres funcoes exigem ponteiros validos; nao testar NULL nelas. */
}

static void one_bit_vectors(void) {
    /* Um unico bit ativo isola cada fronteira sem usar pack como oraculo. */
    for (unsigned bit = 0; bit < 32; ++bit) {
        Header expected = {0, 0, 0, 0}, got = {99, 99, 99, 99};
        uint32_t value = 1;
        unsigned offset = bit;
        if (bit >= 29) offset = bit - 29;
        else if (bit >= 24) offset = bit - 24;
        else if (bit >= 20) offset = bit - 20;
        for (unsigned j = 0; j < offset; ++j) value *= 2;
        if (bit >= 29) expected.version = value;
        else if (bit >= 24) expected.type = value;
        else if (bit >= 20) expected.flags = value;
        else expected.length = value;
        uint32_t word = UINT32_C(1) << bit, packed = 0;
        header_unpack(word, &got);
        same_header(got, expected);
        CHECK(header_pack(&expected, &packed));
        CHECK(packed == word);
        uint8_t bytes[4] = {0, 0, 0, 0};
        uint8_t actual[4] = {0xa5, 0xa5, 0xa5, 0xa5};
        bytes[bit / 8] = (uint8_t)(1u << (bit % 8));
        store_le32(actual, word);
        CHECK(memcmp(actual, bytes, 4) == 0);
        CHECK(load_le32(bytes) == word);
    }
}

static void round_trips(void) {
    static const uint32_t lengths[] = {0, 1, 255, 256, 4095, 4096, 1048574, 1048575};
    for (uint32_t v = 0; v <= 7; ++v)
        for (uint32_t t = 0; t <= 31; ++t)
            for (uint32_t f = 0; f <= 15; ++f)
                for (unsigned i = 0; i < sizeof lengths / sizeof lengths[0]; ++i) {
                    Header input = {v, t, f, lengths[i]}, output = {99,99,99,99};
                    uint32_t word = 0;
                    CHECK(header_pack(&input, &word));
                    header_unpack(word, &output);
                    same_header(input, output);
                }
    static const uint32_t words[] = {0, 1, UINT32_C(0x80000000),
        UINT32_C(0x12345678), UINT32_MAX};
    for (unsigned i = 0; i < sizeof words / sizeof words[0]; ++i) {
        uint8_t bytes[4] = {0xa5, 0xa5, 0xa5, 0xa5};
        store_le32(bytes, words[i]);
        CHECK(load_le32(bytes) == words[i]);
    }
}

int main(void) {
    known_vectors();
    invalid_inputs();
    one_bit_vectors();
    round_trips();
    printf("%u verificacoes; %u falhas\n", checks, failures);
    return failures ? 1 : 0;
}
