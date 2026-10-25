#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile e execute cada caso em processo próprio, com timeout."""
import argparse
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile-only", action="store_true")
    parser.add_argument("--fixture-only", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="oxide-async-") as directory:
        binary = str(Path(directory) / "public")
        compile_result = subprocess.run([
            "rustc", "--edition=2021", "--test", str(ROOT / "checks/public.rs"),
            "-o", binary,
        ], timeout=60)
        if compile_result.returncode:
            return compile_result.returncode
        if args.compile_only:
            print("Preparação: checks e starters compilam; isso não valida os TODOs.")
            return 0
        listing = subprocess.check_output([binary, "--list"], text=True, timeout=5)
        names = [line.removesuffix(": test") for line in listing.splitlines() if line.endswith(": test")]
        if args.fixture_only:
            names = [name for name in names if name.startswith("fixture_")]
        if not names:
            raise RuntimeError("Nenhum check encontrado")
        failures = 0
        for name in names:
            try:
                result = subprocess.run([binary, "--exact", name, "--nocapture"],
                                        timeout=5, capture_output=True, text=True)
            except subprocess.TimeoutExpired:
                print(f"FALHOU {name}: timeout de 5 s; processo encerrado e recolhido")
                failures += 1
                continue
            print(f"{'PASSOU' if result.returncode == 0 else 'FALHOU'} {name}")
            if result.returncode:
                print(result.stdout + result.stderr)
                failures += 1
        print(f"{len(names) - failures}/{len(names)} checks passaram")
        return int(failures != 0)


if __name__ == "__main__":
    raise SystemExit(main())
