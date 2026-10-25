# SPDX-License-Identifier: MIT
CC ?= cc
NVCC ?= nvcc
CFLAGS ?= -O2 -std=c11 -Wall -Wextra -Werror
.PHONY: cpu gpu clean
cpu: build/cpu build/oracle-check
gpu: build/gpu build/probe
build:
	mkdir -p build
build/cpu: cpu.c oracle.c oracle.h | build
	$(CC) $(CFLAGS) cpu.c oracle.c -o $@
build/oracle-check: ../checks/oracle.c oracle.c oracle.h | build
	$(CC) $(CFLAGS) ../checks/oracle.c oracle.c -o $@
build/probe: probe.cu | build
	$(NVCC) -O2 -std=c++14 probe.cu -o $@
build/gpu: runner.cu kernels.cu oracle.c kernels.h oracle.h | build
	$(NVCC) -O2 -std=c++14 runner.cu kernels.cu oracle.c -o $@
clean:
	rm -f build/cpu build/gpu build/oracle-check build/probe
