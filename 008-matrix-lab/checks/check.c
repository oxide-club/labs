/* SPDX-License-Identifier: MIT */
#include "matrix.h"
#include "oracle.h"
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x) do { if(!(x)) {fprintf(stderr,"falhou linha %d\n",__LINE__);return 1;} } while(0)
int main(void) {
 matrix_fn funcs[]={matrix_ijk,matrix_ikj,matrix_blocked};
 double a[]={1,2,3,4,5,6}, b[]={7,8,9,10,11,12};
 double saved_a[6],saved_b[6];
 memcpy(saved_a,a,sizeof a);memcpy(saved_b,b,sizeof b);
 double expected[]={58,64,139,154};
 for(size_t f=0;f<3;f++) {
  double c[]={99,99,99,99};
  CHECK(funcs[f](2,3,2,a,b,c,2)==MATRIX_OK);
  for(size_t z=0;z<4;z++) CHECK(c[z]==expected[z]);
  CHECK(funcs[f](2,3,2,a,b,c,2)==MATRIX_OK); /* sobrescreve */
  CHECK(matches(2,3,2,a,b,c));
  CHECK(!memcmp(a,saved_a,sizeof a) && !memcmp(b,saved_b,sizeof b));
  double aa[15],bb[35],cc[21];
  for(size_t z=0;z<15;z++) aa[z]=((int)(z%7)-3)/4.0;
  for(size_t z=0;z<35;z++) bb[z]=((int)(z%9)-4)/8.0;
  double saved_aa[15],saved_bb[35];
  memcpy(saved_aa,aa,sizeof aa);memcpy(saved_bb,bb,sizeof bb);
  for(size_t tile=1;tile<=8;tile++) {
   for(size_t z=0;z<21;z++) cc[z]=NAN;
   CHECK(funcs[f](3,5,7,aa,bb,cc,tile)==MATRIX_OK);
   CHECK(matches(3,5,7,aa,bb,cc)); /* exige todos finitos */
   CHECK(!memcmp(aa,saved_aa,sizeof aa) && !memcmp(bb,saved_bb,sizeof bb));
  }
  /* Inválido no fim: nenhum elemento de C pode mudar antes da rejeição. */
  for(size_t which=0;which<2;which++) {
   memcpy(aa,saved_aa,sizeof aa);memcpy(bb,saved_bb,sizeof bb);
   if(which==0) aa[14]=NAN; else bb[34]=17;
   double invalid_a[15],invalid_b[35],saved_c[21];
   memcpy(invalid_a,aa,sizeof aa);memcpy(invalid_b,bb,sizeof bb);
   for(size_t z=0;z<21;z++) cc[z]=1000+(double)z;
   memcpy(saved_c,cc,sizeof cc);
   CHECK(funcs[f](3,5,7,aa,bb,cc,2)==MATRIX_INVALID);
   CHECK(!memcmp(cc,saved_c,sizeof cc));
   CHECK(!memcmp(aa,invalid_a,sizeof aa) && !memcmp(bb,invalid_b,sizeof bb));
  }
  double one_a=-16,one_b=16,one_c=9;
  CHECK(funcs[f](1,1,1,&one_a,&one_b,&one_c,256)==MATRIX_OK && one_c==-256);
  one_a=0;
  CHECK(funcs[f](1,1,1,&one_a,&one_b,&one_c,1)==MATRIX_OK && one_c==0);
  /* Valores decimais não exatos em binário expõem arredondamento em acumulador float. */
  double precision_a[300], precision_b[300], precision_c = NAN;
  for(size_t z=0;z<300;z++) { precision_a[z]=0.1; precision_b[z]=0.2; }
  CHECK(funcs[f](1,300,1,precision_a,precision_b,&precision_c,17)==MATRIX_OK);
  CHECK(matches(1,300,1,precision_a,precision_b,&precision_c));
  /* Buffers completos também para implementações que esquecem o limite. */
  double *large_a=calloc(4097,sizeof(double)), *large_b=calloc(4097,sizeof(double));
  double *large_c=malloc(4097*sizeof(double));
  CHECK(large_a && large_b && large_c);
  const size_t dims[3][3]={{4097,1,1},{1,4097,1},{1,1,4097}};
  for(size_t d=0;d<3;d++) {
   for(size_t z=0;z<4097;z++) large_c[z]=123;
   CHECK(funcs[f](dims[d][0],dims[d][1],dims[d][2],large_a,large_b,large_c,1)==MATRIX_INVALID);
   for(size_t z=0;z<4097;z++) CHECK(large_c[z]==123);
  }
  free(large_a);free(large_b);free(large_c);
  double out=123;
  CHECK(funcs[f](0,1,1,a,b,&out,1)==MATRIX_INVALID && out==123);
  CHECK(funcs[f](1,0,1,a,b,&out,1)==MATRIX_INVALID && out==123);
  CHECK(funcs[f](1,1,0,a,b,&out,1)==MATRIX_INVALID && out==123);
  CHECK(funcs[f](SIZE_MAX,2,1,a,b,&out,1)==MATRIX_INVALID && out==123);
  CHECK(funcs[f](1,1,1,NULL,b,&out,1)==MATRIX_INVALID && out==123);
  CHECK(funcs[f](1,1,1,a,NULL,&out,1)==MATRIX_INVALID && out==123);
  CHECK(funcs[f](1,1,1,a,b,NULL,1)==MATRIX_INVALID);
  CHECK(funcs[f](1,1,1,a,b,&out,0)==MATRIX_INVALID && out==123);
  CHECK(funcs[f](1,1,1,a,b,&out,257)==MATRIX_INVALID && out==123);
  double bad=NAN;
  CHECK(funcs[f](1,1,1,&bad,b,&out,1)==MATRIX_INVALID && out==123);
  bad=INFINITY;
  CHECK(funcs[f](1,1,1,a,&bad,&out,1)==MATRIX_INVALID && out==123);
  bad=16.01;
  CHECK(funcs[f](1,1,1,&bad,b,&out,1)==MATRIX_INVALID && out==123);
 }
 puts("checks públicos: OK");return 0;
}
