#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile e verifique a correção; nunca trata falha do runtime como aprovação."""
import argparse
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FLAGS = ["-std=c11", "-Wall", "-Wextra", "-Wpedantic", "-O0", "-g",
         "-fsanitize=address", "-fno-omit-frame-pointer"]


def run(command):
    env = dict(os.environ)
    env["ASAN_OPTIONS"] = "detect_leaks=1:halt_on_error=1:exitcode=99"
    env["LSAN_OPTIONS"] = "exitcode=98"
    return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          env=env, timeout=10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=ROOT / "starter")
    args = parser.parse_args()
    failures = 0
    with tempfile.TemporaryDirectory(prefix="oxide-memory-check-") as tmp:
        binaries = {}
        for name in ("lifetime", "variation"):
            binary = str(Path(tmp) / name)
            subprocess.run(shlex.split(os.environ.get("CC", "cc")) + FLAGS +
                           [str(args.source_dir / (name + ".c")), "-o", binary], check=True)
            binaries[name] = binary
        cases = [("lifetime", [], 0, b"Club\n")]
        cases += [("variation", [arg], 0, expected) for arg, expected in
                  [("0", b"Oxide Club\n"), ("6", b"Club\n"), ("0006", b"Club\n"), ("10", b"\n")]]
        cases += [("variation", argv, 2, b"") for argv in
                  [["11"], ["18446744073709551622"], ["4294967302"], ["-1"], ["+6"], ["6x"], [" 6"], [""],
                   ["9999999999999999999999999999999999999999"], [], ["6", "0"]]]
        for name, argv, status, output in cases:
            result = run([binaries[name]] + argv)
            valid = (result.returncode == status and result.stdout == output and
                     (not result.stderr if status == 0 else
                      result.stderr == b"Erro: use um deslocamento decimal entre 0 e 10.\n"))
            if not valid:
                failures += 1
                print(f"FALHA {name} {argv!r}: status={result.returncode}; "
                      f"stdout={result.stdout!r}")
                print(result.stderr.decode(errors="replace")[:5000], file=sys.stderr)
        print(f"{len(cases)} casos; {failures} falhas")
    return bool(failures)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (subprocess.SubprocessError, OSError) as error:
        print(f"Falha de preparação ou timeout: {error}", file=sys.stderr)
        sys.exit(2)
