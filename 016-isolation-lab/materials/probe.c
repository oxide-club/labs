/* SPDX-License-Identifier: MIT — alvos benignos limitados; somente na VM. */
#define _POSIX_C_SOURCE 200809L
#include "vm_guard.h"
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/resource.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

static void bounded_sleep(void)
{
    struct timespec delay = {2, 0};
    while (nanosleep(&delay, &delay) < 0 && errno == EINTR) {}
}

static int child_case(int orphan)
{
    int ready[2];
    if (pipe(ready) < 0) return 90;
    pid_t child = fork();
    if (child < 0) { close(ready[0]); close(ready[1]); return 90; }
    if (child == 0) {
        close(ready[0]);
        alarm(5); /* alarm não é herdado pelo fork. */
        if (signal(SIGTERM, SIG_IGN) == SIG_ERR) _exit(90);
        if (write(ready[1], "R", 1) != 1) _exit(90);
        close(ready[1]);
        bounded_sleep();
        _exit(0);
    }
    close(ready[1]);
    char byte;
    ssize_t size;
    do { size = read(ready[0], &byte, 1); } while (size < 0 && errno == EINTR);
    close(ready[0]);
    if (size != 1) {
        kill(child, SIGKILL);
        while (waitpid(child, NULL, 0) < 0 && errno == EINTR) {}
        return 90;
    }
    if (orphan) return 7; /* O supervisor deve adotar o filho que permanece. */
    int status;
    pid_t result;
    do { result = waitpid(child, &status, 0); } while (result < 0 && errno == EINTR);
    return result == child && WIFEXITED(status) ? WEXITSTATUS(status) : 90;
}

int main(int argc, char **argv)
{
    if (!vm_confirmed()) return 125;
    alarm(5); /* Limite de emergência da fixture, independente do supervisor. */
    if (argc < 2) return 2;
    if (strcmp(argv[1], "ok") == 0 && argc == 2) return 0;
    if (strcmp(argv[1], "exit7") == 0 && argc == 2) return 7;
    if (strcmp(argv[1], "term") == 0 && argc == 2) { raise(SIGTERM); return 90; }
    if (strcmp(argv[1], "sleep") == 0 && argc == 2) { bounded_sleep(); return 0; }
    if (strcmp(argv[1], "child") == 0 && argc == 2) return child_case(0);
    if (strcmp(argv[1], "orphan") == 0 && argc == 2) return child_case(1);
    if (strcmp(argv[1], "args") == 0 && argc == 5) {
        return strcmp(argv[2], "two words") == 0 && argv[3][0] == '\0'
            && strcmp(argv[4], "; literal") == 0 ? 0 : 91;
    }
    if (strcmp(argv[1], "alloc") == 0 && argc == 2) {
        /* Reserva virtual única de 128 MiB; não toca as páginas. */
        errno = 0;
        void *memory = malloc((size_t)128 * 1024 * 1024);
        if (!memory && errno == ENOMEM) { puts("allocation=denied"); return 0; }
        free(memory);
        return 92;
    }
    if (strcmp(argv[1], "limits") == 0 && argc == 2) {
        struct rlimit as, cpu, core;
        if (getrlimit(RLIMIT_AS, &as) || getrlimit(RLIMIT_CPU, &cpu)
            || getrlimit(RLIMIT_CORE, &core)) return 90;
        /* A bateria exige hard herdado AS >= 64 MiB e CPU >= 1 s.
         * Sob essas precondições, min(teto, hard herdado) é o teto exato. */
        return as.rlim_cur == 67108864 && as.rlim_max == 67108864
            && cpu.rlim_cur == 1 && cpu.rlim_max == 1
            && core.rlim_cur == 0 && core.rlim_max == 0 ? 0 : 93;
    }
    if (strcmp(argv[1], "denied") == 0 && argc == 3) {
        int fd = open(argv[2], O_RDONLY);
        if (fd < 0 && errno == EACCES) { puts("file=denied"); return 0; }
        if (fd >= 0) close(fd);
        return 94;
    }
    if (strcmp(argv[1], "fd") == 0 && argc == 3) {
        char *end;
        long fd = strtol(argv[2], &end, 10);
        if (*end || fd < 3 || fd > 65535) return 2;
        errno = 0;
        return fcntl((int)fd, F_GETFD) == -1 && errno == EBADF ? 0 : 95;
    }
    return 2;
}
