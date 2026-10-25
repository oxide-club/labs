/* SPDX-License-Identifier: MIT */
#include "arithmetic.h"
uint64_t call1(uint64_t a) { return a; }
uint64_t call3(uint64_t a,uint64_t b,uint64_t c) { return a+2*b+3*c; }
uint64_t call6(uint64_t a,uint64_t b,uint64_t c,uint64_t d,uint64_t e,uint64_t f) {
    return a+2*b+3*c+4*d+5*e+6*f;
}
uint64_t call8(uint64_t a,uint64_t b,uint64_t c,uint64_t d,uint64_t e,uint64_t f,uint64_t g,uint64_t h) {
    return a+2*b+3*c+4*d+5*e+6*f+7*g+8*h;
}
