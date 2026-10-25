/* SPDX-License-Identifier: MIT; Oxide Club, 2026. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <link.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

/* Volatile keeps the local array observable without unsafe accesses. */
__attribute__((noinline)) unsigned reference_sum(const char *input) {
    volatile unsigned char local[64];
    size_t n = strlen(input);
    unsigned sum = 0;
    for (size_t i = 0; i < n; ++i) local[i] = (unsigned char)input[i];
    for (size_t i = 0; i < n; ++i) sum += local[i];
    return sum;
}
static int headers(struct dl_phdr_info *info, size_t size, void *data) {
    (void)size; (void)data;
    if (info->dlpi_name[0]) return 0;
    printf("BIAS %lx\n", (unsigned long)info->dlpi_addr);
    for (int i = 0; i < info->dlpi_phnum; ++i) {
        const ElfW(Phdr) *p = &info->dlpi_phdr[i];
        if (p->p_type == PT_GNU_RELRO)
            printf("RELRO %lx %lx\n", (unsigned long)(info->dlpi_addr+p->p_vaddr),
                   (unsigned long)(info->dlpi_addr+p->p_vaddr+p->p_memsz));
    }
    return 1;
}
static int observe(void) {
    int stack_anchor = 0;
    long page = sysconf(_SC_PAGESIZE);
    if (page <= 0) return 3;
    void *region = mmap(NULL, (size_t)page*3, PROT_NONE,
                        MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    if (region == MAP_FAILED) return 3;
    void *anchor = (char *)region+page;
    if (mprotect(anchor, (size_t)page, PROT_READ|PROT_WRITE)) return 3;
    void *libc = dlopen("libc.so.6", RTLD_NOW|RTLD_LOCAL);
    if (!libc) return 3;
    void *symbol = dlsym(libc, "puts");
    Dl_info libinfo;
    if (!symbol || !dladdr(symbol, &libinfo)) return 3;
    printf("PID %ld\nPAGE %ld\n", (long)getpid(), page);
    printf("ANCHOR executable %lx\n", (unsigned long)(uintptr_t)&reference_sum);
    printf("ANCHOR stack %lx\n", (unsigned long)(uintptr_t)&stack_anchor);
    printf("ANCHOR library %lx\n", (unsigned long)(uintptr_t)symbol);
    printf("ANCHOR anonymous %lx\n", (unsigned long)(uintptr_t)anchor);
    printf("LIBRARY %s\n", libinfo.dli_fname);
    dl_iterate_phdr(headers, NULL);
    FILE *maps = fopen("/proc/self/maps", "r");
    if (!maps) return 3;
    char line[4096];
    puts("MAPS");
    while (fgets(line, sizeof line, maps)) fputs(line, stdout);
    int failed = ferror(maps);
    fclose(maps);
    dlclose(libc);
    munmap(region, (size_t)page*3);
    return failed ? 3 : 0;
}
int main(int argc, char **argv) {
    if (argc != 2) { fputs("uso: probe TEXTO | --maps\n", stderr); return 2; }
    if (!strcmp(argv[1], "--maps")) return observe();
    if (strlen(argv[1]) > 63) { fputs("entrada excede 63 bytes\n", stderr); return 2; }
    printf("sum=%u\n", reference_sum(argv[1]));
    return 0;
}
