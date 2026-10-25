/* SPDX-License-Identifier: MIT */
#ifndef MATRIX_H
#define MATRIX_H
#include <stddef.h>
enum { MATRIX_OK=0, MATRIX_INVALID=1, MATRIX_TODO=2 };
/* Contrato integral em materials/README.md. Sem overlap entre buffers. */
typedef int (*matrix_fn)(size_t m,size_t k,size_t n,const double *a,const double *b,double *c,size_t tile);
int matrix_ijk(size_t,size_t,size_t,const double *,const double *,double *,size_t);
int matrix_ikj(size_t,size_t,size_t,const double *,const double *,double *,size_t);
int matrix_blocked(size_t,size_t,size_t,const double *,const double *,double *,size_t);
#endif
