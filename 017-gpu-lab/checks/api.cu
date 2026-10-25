/* SPDX-License-Identifier: MIT */
#include "kernels.h"
#include <cstdio>
#include <stdexcept>
#include <vector>

static void check(cudaError_t status) {
    if (status != cudaSuccess) throw std::runtime_error(cudaGetErrorString(status));
}
struct Buffer {
    long long *data = nullptr;
    explicit Buffer(size_t n) { check(cudaMalloc((void **)&data, n * sizeof(*data))); }
    ~Buffer() { if (data) cudaFree(data); }
};
static void require(bool condition, const char *message) {
    if (!condition) throw std::runtime_error(message);
}
int main() {
    try {
        unsigned cases = 0;
        for (unsigned block : {64u, 128u, 256u, 512u}) {
            for (size_t n : {0u, 1u, 63u, 64u, 65u, 127u, 128u, 129u,
                             255u, 256u, 257u, 511u, 512u, 513u, 4097u}) {
                const size_t count = n ? n : 1;
                std::vector<long long> a(count), b(count), got(count);
                long long expected = 0;
                for (size_t i = 0; i < count; ++i) {
                    a[i] = static_cast<long long>((i * i + 13 * i + 71) % 2049) - 1024;
                    b[i] = i % 2 ? 1024 : -1024;
                    if (i < n) expected += a[i];
                }
                Buffer da(count), db(count), dc(count), sum(1);
                check(cudaMemcpy(da.data, a.data(), count * sizeof(long long), cudaMemcpyHostToDevice));
                check(cudaMemcpy(db.data, b.data(), count * sizeof(long long), cudaMemcpyHostToDevice));
                // Exact allocations expose tail reads to Compute Sanitizer; the
                // runner separately checks sentinel padding for tail writes.
                for (unsigned repeat = 0; repeat < 2; ++repeat) {
                    check(cudaMemset(dc.data, 0x7f, count * sizeof(long long)));
                    check(cudaMemset(sum.data, 0x7f, sizeof(long long)));
                    check(launch_add(da.data, db.data, dc.data, n, block));
                    check(launch_reduce(da.data, sum.data, n, block));
                    check(cudaDeviceSynchronize());
                    check(cudaMemcpy(got.data(), dc.data, count * sizeof(long long), cudaMemcpyDeviceToHost));
                    for (size_t i = 0; i < n; ++i) require(got[i] == a[i] + b[i], "vector mismatch");
                    if (!n) require(got[0] == 0x7f7f7f7f7f7f7f7fLL, "empty add wrote output");
                    long long total;
                    check(cudaMemcpy(&total, sum.data, sizeof(total), cudaMemcpyDeviceToHost));
                    require(total == expected, "reduction mismatch");
                }
                check(cudaMemcpy(got.data(), da.data, count * sizeof(long long), cudaMemcpyDeviceToHost));
                require(got == a, "input a modified");
                check(cudaMemcpy(got.data(), db.data, count * sizeof(long long), cudaMemcpyDeviceToHost));
                require(got == b, "input b modified");
                ++cases;
            }
        }
        std::printf("GPU API: %u cases passed, repeated outputs and unchanged inputs.\n", cases);
        return 0;
    } catch (const std::exception &error) {
        std::fprintf(stderr, "GPU API: %s\n", error.what());
        return 1;
    }
}
