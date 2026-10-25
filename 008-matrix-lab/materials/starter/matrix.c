/* SPDX-License-Identifier: MIT */
#include "matrix.h"
/* Implemente validação e cálculo nas três funções. Não acumule C antigo. */
#define STARTER(name) int name(size_t m,size_t k,size_t n,const double *a,const double *b,double *c,size_t tile) { \
(void)m;(void)k;(void)n;(void)a;(void)b;(void)c;(void)tile; return MATRIX_TODO; }
STARTER(matrix_ijk)
STARTER(matrix_ikj)
STARTER(matrix_blocked)
