#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Registre um único caso defeituoso, com timeout e diretório de saída explícito."""
import argparse
import os
from pathlib import Path
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("output", type=Path, help="diretório novo para binário e diagnóstico")
args = parser.parse_args()
try:
    args.output.mkdir(parents=True, exist_ok=False)
    binary = (args.output / "lifetime").resolve()
    command = shlex.split(os.environ.get("CC", "cc")) + [
        "-std=c11", "-Wall", "-Wextra", "-Wpedantic", "-O0", "-g",
        "-fsanitize=address", "-fno-omit-frame-pointer",
        str(ROOT / "starter/lifetime.c"), "-o", str(binary)]
    subprocess.run(command, check=True, timeout=30)
    env = dict(os.environ)
    env["ASAN_OPTIONS"] = "detect_leaks=1:halt_on_error=1:exitcode=99"
    result = subprocess.run([str(binary)], capture_output=True, env=env, timeout=10)
    (args.output / "stdout.txt").write_bytes(result.stdout)
    (args.output / "asan.txt").write_bytes(result.stderr)
    (args.output / "status.txt").write_text(str(result.returncode) + "\n")
    required = [b"heap-use-after-free", b"freed by", b"previously allocated"]
    if result.returncode == 0 or not all(x in result.stderr for x in required):
        print("Diagnóstico esperado ausente. Examine asan.txt; não conclua ausência de defeito.")
        sys.exit(1)
    print("Use-after-free observado; registre acesso, liberação e alocação em asan.txt.")
except (OSError, subprocess.SubprocessError) as error:
    print(f"Falha de preparação ou timeout: {error}", file=sys.stderr)
    sys.exit(2)
