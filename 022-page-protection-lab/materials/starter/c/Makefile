CC = cc
CFLAGS = -std=c11 -O2 -g -Wall -Wextra -Werror
all: pageprobe
pageprobe: pageprobe.c probe.S probe.h
	$(CC) $(CFLAGS) pageprobe.c probe.S -o $@
probe.o: probe.S
	$(CC) -c probe.S -o $@
audit: probe.o
	objdump -dr probe.o
.PHONY: all audit
