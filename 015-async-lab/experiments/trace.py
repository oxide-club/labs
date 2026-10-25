#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile o experimento e execute com timeout, sem deixar binários no pacote."""
import argparse
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile-only", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="oxide-async-trace-") as directory:
        binary = str(Path(directory) / "trace")
        subprocess.run(["rustc", "--edition=2021",
                        str(Path(__file__).with_suffix(".rs")), "-o", binary],
                       check=True, timeout=60)
        if args.compile_only:
            print("Preparação: experimento compila; execute após completar os TODOs.")
            return 0
        try:
            return subprocess.run([binary], timeout=5).returncode
        except subprocess.TimeoutExpired:
            print("FALHOU: timeout de 5 s; processo encerrado e recolhido")
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
