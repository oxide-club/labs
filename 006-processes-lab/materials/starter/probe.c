/* SPDX-License-Identifier: MIT */
#include <signal.h>

int main(int argc, char **argv)
{
    (void)argv;
    if (argc > 1) {
        signal(SIGTERM, SIG_DFL);
        raise(SIGTERM);
    }
    return 7;
}
