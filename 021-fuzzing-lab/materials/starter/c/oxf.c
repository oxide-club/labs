/* SPDX-License-Identifier: MIT */
#include "oxf.h"
#include <string.h>
static unsigned le16(const uint8_t *p) { return p[0] | ((unsigned)p[1] << 8); }
const char *error_name(Error e) {
 static const char *names[] = {"Ok", "TooLarge", "Truncated", "BadMagic", "BadFlags", "BadCount", "BadPayloadLength", "UnknownType", "BadRecordLength", "BadText", "BadChecksum", "TrailingData"};
 return names[e];
}
Error parse(const uint8_t *b, size_t n, Document *out) {
 if (n > 4096) return TooLarge;
 if (n < 8) return Truncated;
 if (memcmp(b, "OXF1", 4)) return BadMagic;
 if (b[4] & ~1u) return BadFlags;
 if (b[5] > 16) return BadCount;
 size_t length = le16(b+6), end = 8+length;
 if (length > 256) return BadPayloadLength;
 size_t total = end + ((b[4]&1) ? 2 : 0);
 if (n < total) return Truncated;
 if (n > total) return TrailingData;
 Document d = {0};
 d.count = b[5]; d.checksum = b[4]&1;
 size_t pos = 8;
 for (unsigned i=0; i<d.count; ++i) {
  if (end-pos < 2) return Truncated;
  Record *r = &d.records[i];
  r->type = b[pos++]; r->len = b[pos++];
  if (r->type != 1 && r->type != 2) return UnknownType;
  if ((r->type == 1 && r->len != 2) || (r->type == 2 && r->len > 32)) return BadRecordLength;
  if (r->type == 1) d.sum = (uint16_t)(d.sum + le16(b+pos));
  if (r->len > end-pos) return Truncated;
  if (r->type == 2)
   for (unsigned j=0; j<r->len; ++j)
    if (b[pos+j] < 0x20 || b[pos+j] > 0x7e) return BadText;
  memcpy(r->data, b+pos, r->len); pos += r->len;
 }
 if (pos != end) return BadCount;
 if (d.checksum) {
  unsigned sum = 0;
  for (size_t j=8; j<end; ++j) sum += b[j];
  if ((sum & 65535) != le16(b+end)) return BadChecksum;
 }
 *out = d; return Ok;
}
