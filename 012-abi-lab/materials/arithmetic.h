/* SPDX-License-Identifier: MIT */
#ifndef ARITHMETIC_H
#define ARITHMETIC_H
#include <stdint.h>
uint64_t call1(uint64_t);
uint64_t call3(uint64_t,uint64_t,uint64_t);
uint64_t call6(uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t);
uint64_t call8(uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t);
uint64_t arithmetic8(uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t);
void alignment_probe(void);
extern uint64_t probe_count, probe_alignment;
uint64_t invoke_checked(const uint64_t *, uint64_t *);
#endif
