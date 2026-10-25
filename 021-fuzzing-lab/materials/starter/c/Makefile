CC = clang
CFLAGS = -std=c11 -g -O1 -Wall -Wextra -Werror -fno-omit-frame-pointer -fsanitize=address,undefined -fno-sanitize-recover=all
BUILD ?= build
PARSER ?= oxf.c
.PHONY: all fuzz
all: $(BUILD)/runner
$(BUILD):
	mkdir -p $(BUILD)
$(BUILD)/runner: $(PARSER) runner.c oxf.h | $(BUILD)
	$(CC) $(CFLAGS) -I. $(PARSER) runner.c -o $@
fuzz: | $(BUILD)
	$(CC) $(CFLAGS) -fsanitize=fuzzer -I. $(PARSER) fuzz_target.c -o $(BUILD)/fuzz
