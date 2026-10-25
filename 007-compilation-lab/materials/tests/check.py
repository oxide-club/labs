# SPDX-License-Identifier: MIT
"""Checks de comportamento; não avaliam o relato."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

build = Path(sys.argv[1] if len(sys.argv) > 1 else "build").resolve()

def run(args, **kwargs):
    return subprocess.run(args, capture_output=True, timeout=10, **kwargs)

exe = str(build / "program")
for args, data, status, output in [([], b"", 0, b"oxide result=12\n"),
                                 (["--wait"], b"x", 0, b"oxide result=12\n"),
                                 (["--wait"], b"", 0, b"oxide result=12\n"),
                                 (["bad"], b"", 2, b""),
                                 (["--wait", "bad"], b"", 2, b"")]:
    result = run([exe, *args], input=data)
    assert (result.returncode, result.stdout) == (status, output), result
    assert bool(result.stderr) == (status == 2), result
# Linux: /dev/full rejeita escritas sem introduzir SIGPIPE.
with open("/dev/full", "wb") as full:
    result = subprocess.run([exe, "bad"], input=b"", stdout=subprocess.PIPE,
                            stderr=full, timeout=10)
assert (result.returncode, result.stdout) == (1, b""), result
for module in ("main", "operations"):
    for suffix in ("i", "s", "o"):
        assert (build / f"{module}.{suffix}").stat().st_size > 0
assert (build / "main.o").read_bytes()[:4] == b"\x7fELF"
assert (build / "program").read_bytes()[:4] == b"\x7fELF"
undefined = run(["nm", "-u", str(build / "main.o")])
assert undefined.returncode == 0 and b"add_global" in undefined.stdout
with tempfile.TemporaryDirectory(prefix="oxide-link-") as temp:
    for label, objects, symbol in [
        ("undefined", ["main.o"], b"add_global"),
        ("duplicate", ["main.o", "operations.o", "operations.o"], b"global_value")]:
        result = run([os.environ.get("CC", "cc"),
                      *(str(build / name) for name in objects), "-o", f"{temp}/{label}"])
        assert result.returncode != 0 and symbol in result.stderr, result
        (build / f"{label}.stderr.txt").write_bytes(result.stderr)
        print(f"{label}: falha de linking esperada (status {result.returncode})")
print("OK: saída, status, EOF, artefatos, símbolo indefinido e dois erros de linking")
