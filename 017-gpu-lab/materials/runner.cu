/* SPDX-License-Identifier: MIT */
#include "kernels.h"
#include "oracle.h"
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <stdexcept>
#include <vector>
#include <string>
#include <cstring>
static void check(cudaError_t e) {
    if (e != cudaSuccess) throw std::runtime_error(cudaGetErrorString(e));
}
struct Buffer {
    long long *p = nullptr;
    explicit Buffer(size_t n) { check(cudaMalloc((void **)&p, n * sizeof(*p))); }
    void release() {
        if (p) { check(cudaFree(p)); p = nullptr; }
    }
    ~Buffer() noexcept { if (p && cudaFree(p) != cudaSuccess) std::fprintf(stderr, "cudaFree falhou\n"); }
};
struct Event {
    cudaEvent_t e = nullptr;
    Event() { check(cudaEventCreate(&e)); }
    void release() {
        if (e) { check(cudaEventDestroy(e)); e = nullptr; }
    }
    ~Event() noexcept { if (e && cudaEventDestroy(e) != cudaSuccess) std::fprintf(stderr, "cudaEventDestroy falhou\n"); }
};
using Clock = std::chrono::steady_clock;
static double ms(Clock::time_point a, Clock::time_point b) {
    return std::chrono::duration<double, std::milli>(b-a).count();
}
static unsigned number(const char *s, unsigned maximum) {
    if (!*s || *s == '-') throw std::invalid_argument("inteiro fora da faixa");
    char *end; unsigned long v = std::strtoul(s, &end, 10);
    if (*end || v > maximum) throw std::invalid_argument("inteiro fora da faixa");
    return static_cast<unsigned>(v);
}
int main(int argc, char **argv) {
    try {
        if (argc != 4 && argc != 5) return 2;
        int mode = 0;
        unsigned n, block, seed;
        try {
            if (argc == 5) {
                if (std::strcmp(argv[4], "positive") == 0) mode = 1;
                else if (std::strcmp(argv[4], "negative") == 0) mode = -1;
                else if (std::strcmp(argv[4], "ramp") == 0) mode = 2;
                else throw std::invalid_argument("modo deve ser positive, negative ou ramp");
            }
            n = number(argv[1], MAX_N); block = number(argv[2], 512); seed = number(argv[3], 1000);
            if (block != 64 && block != 128 && block != 256 && block != 512)
                throw std::invalid_argument("bloco deve ser 64, 128, 256 ou 512");
        } catch (const std::invalid_argument &e) { std::fprintf(stderr, "%s\n", e.what()); return 2; }
        int device; check(cudaGetDevice(&device));
        cudaDeviceProp prop; check(cudaGetDeviceProperties(&prop, device));
        if (block > static_cast<unsigned>(prop.maxThreadsPerBlock))
            throw std::runtime_error("bloco excede limite da GPU");
        int runtime, driver; check(cudaRuntimeGetVersion(&runtime)); check(cudaDriverGetVersion(&driver));
        std::fprintf(stderr, "GPU=%s runtime=%d driver=%d\n", prop.name, runtime, driver);
        // Uma região extra detecta threads que acessam o tail como dados válidos.
        // O padding não pertence à entrada lógica entregue aos kernels.
        const size_t count = static_cast<size_t>(n) + block, bytes = static_cast<size_t>(n) * sizeof(long long);
        const long long sentinel = 0x7f7f7f7f7f7f7f7fLL;
        std::vector<long long> a(count, 19), b(count, 23), expected(count), got(count);
        if (mode) {
            for (size_t i=0; i<n; ++i) a[i] = b[i] = mode == 2 ? 1024LL - (i % 7) : mode * 1024LL;
        } else generate(a.data(), b.data(), n, seed);
        const long long expected_sum = oracle(a.data(), b.data(), expected.data(), n);
        if (mode == 2 && n == MAX_N && expected_sum != 4282385411LL)
            throw std::runtime_error("oráculo diverge da rampa inteira");
        if (mode == 1 || mode == -1) {
            if (expected_sum != mode * static_cast<long long>(n) * 1024LL ||
                (n == MAX_N && expected_sum != mode * 4294968320LL))
                throw std::runtime_error("oráculo diverge do extremo constante");
            for (size_t i=0; i<n; ++i)
                if (expected[i] != mode * 2048LL) throw std::runtime_error("oráculo vetorial diverge do extremo");
        }
        Buffer da(count), db(count), dc(count), ds(1);
        Event start, stop;
        auto run = [&](bool timed) {
            // Contexto, allocation e geração ficam fora do total; todas as operações usam o stream padrão.
            // 0x7f em todos os bytes fica fora das faixas válidas do vetor e da reduction.
            // Invalide a saída também após o aquecimento: resultados antigos não podem passar.
            check(cudaMemset(dc.p, 0x7f, count * sizeof(long long)));
            check(cudaMemset(ds.p, 0x7f, sizeof(long long)));
            // Padding de diagnóstico preparado fora das transferências medidas.
            check(cudaMemcpy(da.p + n, a.data() + n, block * sizeof(long long), cudaMemcpyHostToDevice));
            check(cudaMemcpy(db.p + n, b.data() + n, block * sizeof(long long), cudaMemcpyHostToDevice));
            check(cudaDeviceSynchronize());
            const auto begin = Clock::now();
            check(cudaMemcpy(da.p, a.data(), bytes, cudaMemcpyHostToDevice));
            check(cudaMemcpy(db.p, b.data(), bytes, cudaMemcpyHostToDevice));
            const auto copied = Clock::now();
            if (timed) check(cudaEventRecord(start.e));
            check(launch_add(da.p, db.p, dc.p, n, block)); check(cudaGetLastError());
            check(launch_reduce(da.p, ds.p, n, block)); check(cudaGetLastError());
            if (timed) check(cudaEventRecord(stop.e));
            check(cudaDeviceSynchronize());
            const auto kernels_done = Clock::now();
            long long sum;
            check(cudaMemcpy(got.data(), dc.p, bytes, cudaMemcpyDeviceToHost));
            check(cudaMemcpy(&sum, ds.p, sizeof(sum), cudaMemcpyDeviceToHost));
            const auto end = Clock::now();
            check(cudaMemcpy(got.data() + n, dc.p + n, block * sizeof(long long), cudaMemcpyDeviceToHost));
            if (sum != expected_sum) throw std::runtime_error("redução diverge da CPU");
            for (size_t i=0; i<n; ++i)
                if (got[i] != expected[i]) throw std::runtime_error("soma vetorial diverge da CPU");
            for (size_t i=n; i<count; ++i)
                if (got[i] != sentinel) throw std::runtime_error("escrita no padding após o tail");
            if (timed) {
                float kernel; check(cudaEventElapsedTime(&kernel, start.e, stop.e));
                std::printf("%u,%u,%u,%.6f,%.6f,%.6f,%.6f\n", n, block, seed,
                            kernel, ms(begin,copied), ms(kernels_done,end), ms(begin,end));
            }
        };
        run(false); // Correção e aquecimento antes de iniciar qualquer temporização publicada.
        std::puts("n,block,seed,kernel_ms,h2d_ms,d2h_ms,total_ms");
        run(true); // A amostra medida também deve produzir resultados corretos.
        stop.release(); start.release();
        ds.release(); dc.release(); db.release(); da.release();
        return 0;
    } catch (const std::exception &e) { std::fprintf(stderr, "%s\n", e.what()); return 1; }
}
