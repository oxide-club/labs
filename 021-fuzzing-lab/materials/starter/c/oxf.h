/* SPDX-License-Identifier: MIT */
#ifndef OXF_H
#define OXF_H
#include <stddef.h>
#include <stdint.h>
typedef enum { Ok, TooLarge, Truncated, BadMagic, BadFlags, BadCount,
 BadPayloadLength, UnknownType, BadRecordLength, BadText, BadChecksum,
 TrailingData } Error;
typedef struct { uint8_t type, len, data[32]; } Record;
typedef struct { uint8_t count, checksum; uint32_t sum; Record records[16]; } Document;
/* out obrigatório; data pode ser NULL apenas quando size == 0.
 * Saída só é utilizável após Ok. Sem estado global ou propriedade transferida. */
Error parse(const uint8_t *data, size_t size, Document *out);
const char *error_name(Error error);
#endif
