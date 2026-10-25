# SPDX-License-Identifier: MIT
"""Coleta local com PID próprio e espera limitada."""
from pathlib import Path
import os
import select
import shutil
import subprocess
import sys

build = Path(sys.argv[1] if len(sys.argv) > 1 else "build").resolve()
exe = str(build / "program")
for name, command in [
    ("symbols", ["nm", str(build / "main.o"), str(build / "operations.o"), exe]),
    ("object", ["readelf", "-hSWsr", str(build / "main.o")]),
    ("elf", ["readelf", "-hSWlsrd", exe]),
    ("disassembly", ["objdump", "-dr", str(build / "main.o")])]:
    result = subprocess.run(command, capture_output=True, timeout=10, check=True)
    (build / f"{name}.txt").write_bytes(result.stdout)

# O pipe permanece aberto até depois da leitura de maps.
process = subprocess.Popen([exe, "--wait"], stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
try:
    if not select.select([process.stdout], [], [], 5)[0]:
        raise TimeoutError("program não sinalizou prontidão em cinco segundos")
    line = os.read(process.stdout.fileno(), 4096)
    if line != b"oxide result=12\n" or process.poll() is not None:
        raise RuntimeError(f"prontidão inválida: {line!r}")
    maps = Path(f"/proc/{process.pid}/maps").read_bytes()
    if exe.encode() not in maps:
        raise RuntimeError("maps não contém o executável próprio")
    (build / "maps.txt").write_bytes(maps)
    process.stdin.close()
    if process.wait(timeout=5) != 0:
        raise RuntimeError("program terminou com erro")
finally:
    if process.poll() is None:
        process.kill()
    process.wait()
    for stream in (process.stdin, process.stdout, process.stderr):
        stream.close()
print("OK: símbolos, ELF, disassembly e maps do processo próprio")
trace = build / "strace.txt"
trace.unlink(missing_ok=True)
if shutil.which("strace"):
    result = subprocess.run(["strace", "--kill-on-exit", "-o", str(trace), "-e",
                             "trace=execve,openat,mmap,mprotect,read,write,exit_group", exe],
                            capture_output=True, timeout=10)
    (build / "strace-status.txt").write_text(
        f"status={result.returncode}\n" + result.stderr.decode(errors="replace"))
    if result.returncode:
        raise SystemExit("strace falhou; veja strace-status.txt; coleta pendente")
    print("OK: trace filtrado a execve/openat/mmap/mprotect/read/write/exit_group; anote os eventos")
else:
    (build / "strace-status.txt").write_text("PENDENTE: strace não está instalado\n")
    print("PENDENTE: strace não está instalado; coleta parcial")
