/* SPDX-License-Identifier: MIT */
#include "write_api.h"
#include <errno.h>
#include <unistd.h>
int write_all(int fd, const void *buf, size_t length) {
    const unsigned char *bytes = buf;
    size_t done = 0;
    while (done < length) {
        ssize_t result = write(fd, bytes + done, length - done);
        if (result > 0) done += (size_t) result;
        else if (result < 0 && errno == EINTR) continue;
        else {
            if (result == 0) errno = EIO;
            return -1;
        }
    }
    return 0;
}
#include "driver.h"
