/* SPDX-License-Identifier: MIT */
#include <stdio.h>
int oxide_add(int a, int b) { return a + b; }
__attribute__((destructor)) static void closed(void) { puts("fixture-closed"); }
