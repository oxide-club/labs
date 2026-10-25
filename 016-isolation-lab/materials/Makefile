# SPDX-License-Identifier: MIT
CC ?= cc
CFLAGS ?= -std=c11 -Wall -Wextra -Werror -pedantic -O2
BUILD ?= build

.PHONY: all static-check
all: $(BUILD)/supervisor $(BUILD)/probe

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/supervisor: supervisor.c vm_guard.h | $(BUILD)
	$(CC) $(CFLAGS) supervisor.c -o $@

$(BUILD)/probe: probe.c vm_guard.h | $(BUILD)
	$(CC) $(CFLAGS) probe.c -o $@

static-check:
	$(CC) $(CFLAGS) -fsyntax-only supervisor.c probe.c

# Não há alvo run/check: execução exige confirmação explícita dentro da VM.
