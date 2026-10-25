CC = cc
BUILD ?= build
FLAGS = -std=c11 -O0 -g -Wall -Wextra -Wpedantic
.PHONY: all check observe
all: $(BUILD)/program
$(BUILD):
	mkdir -p $(BUILD)
$(BUILD)/%.i: starter/%.c starter/operations.h | $(BUILD)
	$(CC) $(FLAGS) -E $< -o $@
$(BUILD)/%.s: $(BUILD)/%.i
	$(CC) $(FLAGS) -S $< -o $@
$(BUILD)/%.o: $(BUILD)/%.s
	$(CC) -c $< -o $@
$(BUILD)/program: $(BUILD)/main.o $(BUILD)/operations.o
	$(CC) $^ -o $@
check: all
	python3 tests/check.py $(BUILD)
observe: all
	python3 experiments/observe.py $(BUILD)
.SECONDARY:
