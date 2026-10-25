/* SPDX-License-Identifier: MIT */
#include <cuda_runtime.h>
#include <cstdio>
static bool ok(cudaError_t e) {
    if (e == cudaSuccess) return true;
    std::fprintf(stderr, "%s\n", cudaGetErrorString(e));
    return false;
}
int main() {
    int device, runtime, driver;
    cudaDeviceProp prop;
    if (!ok(cudaGetDevice(&device)) || !ok(cudaGetDeviceProperties(&prop, device)) ||
        !ok(cudaRuntimeGetVersion(&runtime)) || !ok(cudaDriverGetVersion(&driver))) return 1;
    long long input[3] = {-1024, 0, 1024}, output[3] = {0,0,0}, *buffer = nullptr;
    if (!ok(cudaMalloc((void **)&buffer, sizeof(input)))) return 1;
    bool passed = ok(cudaMemcpy(buffer,input,sizeof(input),cudaMemcpyHostToDevice));
    if (passed) passed = ok(cudaMemcpy(output,buffer,sizeof(output),cudaMemcpyDeviceToHost));
    if (passed) passed = ok(cudaDeviceSynchronize());
    const bool released = ok(cudaFree(buffer));
    for (int i=0; i<3; ++i) if (input[i] != output[i]) passed = false;
    if (!passed || !released) return 1;
    std::printf("GPU=%s runtime=%d driver=%d: alocação e cópias verificadas; nenhum kernel testado.\n",
                prop.name, runtime, driver);
    return 0;
}
