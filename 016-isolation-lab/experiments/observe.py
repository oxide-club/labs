"""SPDX-License-Identifier: MIT — inventário somente leitura dentro da VM."""
from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
from vm import require_vm


def main():
    require_vm(sys.argv[1:])
    print(f"kernel={os.uname().release} uid={os.getuid()}")
    for namespace in ("user", "pid", "mnt", "net", "cgroup"):
        path = Path("/proc/self/ns") / namespace
        try:
            print(f"{namespace}={os.readlink(path)}")
        except OSError as error:
            print(f"{namespace}: indisponível ({error})")
    for name in ("/proc/self/cgroup", "/sys/fs/cgroup/cgroup.controllers"):
        try:
            print(f"{name}:\n{Path(name).read_text()}")
        except OSError as error:
            print(f"{name}: indisponível ({error})")
    for line in Path("/proc/self/status").read_text().splitlines():
        if line.startswith(("NoNewPrivs:", "Seccomp:", "CapEff:")):
            print(line)


if __name__ == "__main__":
    main()
