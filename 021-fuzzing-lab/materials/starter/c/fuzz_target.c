/* SPDX-License-Identifier: MIT */
#include "oxf.h"
#ifndef PARTICIPANT_TARGET_READY
#error "Implemente o target e defina PARTICIPANT_TARGET_READY antes de compilar."
#endif
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
 /* TODO: chame o parser; confira invariantes, determinismo e oráculo.
  * Não faça I/O nem encerre por rejeição legítima. */
 (void)data; (void)size;
 return 0;
}
