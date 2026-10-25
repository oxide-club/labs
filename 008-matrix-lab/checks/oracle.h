/* SPDX-License-Identifier: MIT */
#ifndef ORACLE_H
#define ORACLE_H
#include <math.h>
#include <stddef.h>
/* Oráculo de verificação: soma escalar em long double, sem medir desempenho. */
static int matches(size_t m,size_t k,size_t n,const double *a,const double *b,const double *c) {
 for(size_t row=0;row<m;row++) for(size_t col=0;col<n;col++) {
  long double sum=0;
  for(size_t q=0;q<k;q++) sum+=(long double)a[row*k+q]*b[q*n+col];
  if(!isfinite(c[row*n+col]) || fabsl(c[row*n+col]-sum)>1e-6L+1e-10L*fabsl(sum)) return 0;
 }
 return 1;
}
#endif
