"""SPDX-License-Identifier: MIT — guarda compartilhada dos comandos de execução."""
import os
import sys


def require_vm(arguments):
    if arguments != ["--confirm-disposable-vm"] or os.environ.get("OXIDE_DISPOSABLE_VM") != "confirmed":
        raise SystemExit("Recusa: use uma VM descartável; a confirmação exige a variável e --confirm-disposable-vm.")
    if sys.platform != "linux" or os.geteuid() == 0:
        raise SystemExit("Recusa: o roteiro exige Linux e usuário sem privilégios dentro da VM.")
