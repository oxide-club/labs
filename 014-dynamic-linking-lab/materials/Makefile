# SPDX-License-Identifier: MIT
CC = cc
CFLAGS = -std=c11 -Wall -Wextra -Werror -O0 -g
all: build/archive-client build/shared-client build/dynamic build/broken.so build/renamed.so build/lifetime.so build/dynamic-lifetime
build:
	mkdir -p build
build/library.o: library.c library.h | build
	$(CC) $(CFLAGS) -fPIC -c library.c -o $@
build/liboxide.a: build/library.o
	ar rcs $@ $<
build/liboxide.so: build/library.o
	$(CC) -shared -Wl,-soname,liboxide.so -o $@ $<
build/archive-client: client.c library.h build/liboxide.a
	$(CC) $(CFLAGS) client.c build/liboxide.a -o $@
build/shared-client: client.c library.h build/liboxide.so
	$(CC) $(CFLAGS) client.c -Lbuild -loxide -Wl,-rpath,'$$ORIGIN' -o $@
build/dynamic: dynamic.c | build
	$(CC) $(CFLAGS) dynamic.c -ldl -o $@
build/broken.so: ../experiments/broken.c | build
	$(CC) $(CFLAGS) -fPIC -shared -Wl,-z,lazy $< -o $@
build/renamed.so: ../experiments/renamed.c | build
	$(CC) $(CFLAGS) -fPIC -shared $< -o $@
.PHONY: all

build/lifetime.so: ../checks/lifetime.c | build
	$(CC) $(CFLAGS) -fPIC -shared $< -o $@
build/dynamic-lifetime: dynamic.c ../checks/close.c | build
	$(CC) $(CFLAGS) $^ -Wl,--wrap=dlclose -Wl,--wrap=dlerror -ldl -o $@
