# SPDX-License-Identifier: MIT
CC = cc
CFLAGS = -std=c11 -Wall -Wextra -Werror -O0 -g
BUILD ?= build
BACKEND_libc = -DEXPECT_LIBC
BACKEND_syscall = -DEXPECT_SYSCALL
.PHONY: all libc-check check
all: $(BUILD)/write_libc $(BUILD)/write_syscall
$(BUILD):
	mkdir -p $@
$(BUILD)/write_%: starter/write_%.c starter/write_api.h starter/driver.h | $(BUILD)
	$(CC) $(CFLAGS) $< -o $@
$(BUILD)/contract_%: starter/write_%.c starter/write_api.h ../checks/contract.c | $(BUILD)
	$(CC) $(CFLAGS) -DLAB_NO_MAIN $(BACKEND_$*) -Istarter $< ../checks/contract.c -Wl,--wrap=write -Wl,--wrap=syscall -o $@
libc-check: $(BUILD)/write_libc $(BUILD)/contract_libc
	timeout 5s $(BUILD)/contract_libc
	python3 ../checks/cli.py $(BUILD)/write_libc
check: all $(BUILD)/contract_libc $(BUILD)/contract_syscall
	timeout 5s $(BUILD)/contract_libc
	timeout 5s $(BUILD)/contract_syscall
	python3 ../checks/cli.py $(BUILD)/write_libc $(BUILD)/write_syscall
