/* SPDX-License-Identifier: MIT */
#define _POSIX_C_SOURCE 200809L
#include "matrix.h"
#include "oracle.h"
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
static double now(void){struct timespec t;if(clock_gettime(CLOCK_MONOTONIC,&t))exit(2);return t.tv_sec+t.tv_nsec*1e-9;}
static uint32_t state;
static double value(void){state=state*1664525u+1013904223u;return ((int)(state%2049)-1024)/1024.0;}
static size_t number(const char *s,size_t lo,size_t hi){char *e;errno=0;if(!*s)exit(2);for(const char *q=s;*q;q++)if(*q<'0'||*q>'9')exit(2);unsigned long long v=strtoull(s,&e,10);if(errno||*e||v<lo||v>hi)exit(2);return (size_t)v;}
static void poison(double *c,size_t count){for(size_t z=0;z<count;z++)c[z]=NAN;}
static const char *meta(const char *key){const char *s=getenv(key);if(!s||!*s)exit(2);for(const char *q=s;*q;q++)if(*q=='"'||*q=='\n'||*q=='\r')exit(2);return s;}
int main(int argc,char **argv){
 if(argc!=8){fprintf(stderr,"uso: benchmark M K N TILE SEED WARMUPS REPS\n");return 2;}
 size_t m=number(argv[1],1,4096),k=number(argv[2],1,4096),n=number(argv[3],1,4096),tile=number(argv[4],1,256);
 size_t seed=number(argv[5],0,UINT32_MAX),warm=number(argv[6],1,100),reps=number(argv[7],3,1000);
 const char *hardware=meta("MATRIX_HARDWARE"),*flags=meta("MATRIX_FLAGS"),*compiler=meta("MATRIX_COMPILER");
 double *a=malloc(m*k*sizeof *a),*b=malloc(k*n*sizeof *b),*c=malloc(m*n*sizeof *c);
 if(!a||!b||!c){free(a);free(b);free(c);return 2;}
 state=(uint32_t)seed;for(size_t z=0;z<m*k;z++)a[z]=value();for(size_t z=0;z<k*n;z++)b[z]=value();
 matrix_fn funcs[]={matrix_ijk,matrix_ikj,matrix_blocked};const char *names[]={"ijk","ikj","blocked"};
 /* Nenhum CSV/tempo antes da validação de TODAS as variantes. */
 for(size_t f=0;f<3;f++){poison(c,m*n);if(funcs[f](m,k,n,a,b,c,tile)!=MATRIX_OK||!matches(m,k,n,a,b,c)){fprintf(stderr,"validação falhou: %s\n",names[f]);free(a);free(b);free(c);return 1;}}
 puts("variant,m,k,n,tile,seed,warmups,repetitions,repetition,seconds,threads,compiler,flags,hardware");
 for(size_t f=0;f<3;f++){
  for(size_t r=0;r<warm;r++)if(funcs[f](m,k,n,a,b,c,tile))return 1;
  for(size_t r=0;r<reps;r++){poison(c,m*n);double start=now();int status=funcs[f](m,k,n,a,b,c,tile);double elapsed=now()-start;
   if(status||!matches(m,k,n,a,b,c))return 1;
   printf("%s,%zu,%zu,%zu,%zu,%zu,%zu,%zu,%zu,%.9g,1,\"%s\",\"%s\",\"%s\"\n",names[f],m,k,n,tile,seed,warm,reps,r,elapsed,compiler,flags,hardware);
  }
 }
 free(a);free(b);free(c);return 0;
}
