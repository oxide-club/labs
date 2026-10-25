/* SPDX-License-Identifier: MIT */
#ifndef PAGEPROBE_H
#define PAGEPROBE_H
unsigned probe_read(const void *address);
void probe_write(void *address);
#endif
