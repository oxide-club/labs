/* SPDX-License-Identifier: MIT */
#include "oxf.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* Uma linha hexadecimal por chamada; linha vazia representa zero bytes.
 * O runner faz I/O; o parser e o target não fazem. */
int main(void) {
 char line[8200];
 while (fgets(line, sizeof line, stdin)) {
  size_t chars=0; while (line[chars] && line[chars]!='\n') ++chars;
  if (chars%2 || chars>8194 || strspn(line,"0123456789abcdefABCDEF")!=chars) return 2;
  size_t n=chars/2; uint8_t *b=n ? malloc(n) : NULL;
  if (n && !b) return 2;
  for (size_t i=0;i<n;++i) {
   unsigned v; char pair[3]={line[2*i],line[2*i+1],0};
   if (sscanf(pair,"%2x",&v)!=1) {free(b);return 2;} b[i]=(uint8_t)v;
  }
  Document d; Error e=parse(b,n,&d); free(b);
  if(e!=Ok) {puts(error_name(e));continue;}
  printf("Ok %u %u %u",d.checksum,d.sum,d.count);
  for(unsigned i=0;i<d.count;++i) {
   printf(" %u:",d.records[i].type);
   for(unsigned j=0;j<d.records[i].len;++j) printf("%02x",d.records[i].data[j]);
  }
  puts("");
 }
 return ferror(stdin) ? 2 : 0;
}
