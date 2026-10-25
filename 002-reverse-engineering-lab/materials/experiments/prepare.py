# SPDX-License-Identifier: MIT
"""Compile O0; --optimized acrescenta O2 apenas na extensão."""
import argparse
from pathlib import Path
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="diretório local de trabalho")
    parser.add_argument("--optimized", action="store_true", help="extensão: gerar também O2 após a análise")
    args = parser.parse_args()
    work = args.directory.resolve()
    work.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).resolve().parents[1] / "source-archive" / "gate.c"
    guarded = work / "source-archive"
    guarded.mkdir(exist_ok=True)
    target_source = guarded / "gate.c"
    if source != target_source:
        shutil.copyfile(source, target_source)
    for level in (("O0", "O2") if args.optimized else ("O0",)):
        name = "gate-" + level
        command = ["gcc", "-std=c11", "-Wall", "-Wextra", "-Wpedantic",
                   "-" + level, "-g", "-fno-omit-frame-pointer",
                   "source-archive/gate.c", "-o", name]
        print(" ".join(command), flush=True)
        subprocess.run(command, cwd=work, check=True)
        with (work / (name + ".txt")).open("w") as output:
            subprocess.run(["objdump", "-d", "./" + name], cwd=work,
                           stdout=output, check=True)
    archived = work / "source-after-analysis"
    archived.mkdir(exist_ok=True)
    target_source.replace(archived / "gate.c")
    print("Artefatos em", work)


if __name__ == "__main__":
    main()
