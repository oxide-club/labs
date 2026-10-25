CC = cc
CFLAGS = -std=c11 -Wall -Wextra -Wpedantic -O0 -g
BUILD ?= build

.PHONY: all check clean
all: $(BUILD)/oxrun $(BUILD)/probe
$(BUILD):
	mkdir -p $@
$(BUILD)/oxrun: starter/oxrun.c | $(BUILD)
	$(CC) $(CFLAGS) $< -o $@
$(BUILD)/probe: starter/probe.c | $(BUILD)
	$(CC) $(CFLAGS) $< -o $@
check: all
	python3 tests/check.py --oxrun $(BUILD)/oxrun --probe $(BUILD)/probe
clean:
	rm -rf $(BUILD)
