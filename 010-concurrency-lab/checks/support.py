# SPDX-License-Identifier: MIT
import os
import signal
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def compile_c(output, sources, tsan=False, extra=()):
    flags = ["-fsanitize=thread", "-g", "-O1"] if tsan else ["-O2"]
    command = [os.environ.get("CC", "cc"), "-std=c11", "-Wall", "-Wextra",
               "-Wpedantic", "-pthread", *flags, "-I", str(ROOT / "materials/starter"),
               *(str(ROOT / source) for source in sources), *extra, "-o", str(output)]
    # O driver pode iniciar cc1/assembler/linker: cada compilação possui seu grupo.
    process = subprocess.Popen(command, start_new_session=True)
    try:
        code = process.wait(timeout=60)
    except BaseException:
        # Inclui timeout e KeyboardInterrupt. O PGID foi criado por este Popen.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        raise
    if code:
        raise subprocess.CalledProcessError(code, command)


def run_owned(command, timeout=15):
    """Estes alvos criam threads, não processos descendentes."""
    process = subprocess.Popen([str(x) for x in command], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True)
    try:
        try:
            out, err = process.communicate(timeout=timeout)
            return process.returncode, out, err, False
        except subprocess.TimeoutExpired:
            process.kill()
            out, err = process.communicate()
            return process.returncode, out, err, True
    finally:
        # Também executa reaping em Ctrl-C/exceção. Não procura nem mata processos alheios.
        if process.poll() is None:
            process.kill()
        process.wait()
