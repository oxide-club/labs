"""SPDX-License-Identifier: MIT — checks públicos, somente em VM descartável.

O reaping de emergência detecta falhas; não faz parte da solução do supervisor.
"""
import ctypes
import argparse
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile
import time

from vm import require_vm

ROOT = Path(__file__).resolve().parents[1]
SUPERVISOR = ROOT / "materials/build/supervisor"
PROBE = ROOT / "materials/build/probe"


def children():
    return [int(pid) for pid in Path(f"/proc/self/task/{os.getpid()}/children").read_text().split()]


def cleanup_adopted():
    """Somente filhos próprios, mantidos identificáveis até waitpid; nunca killpg."""
    observed = set()
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        current = children()
        if not current:
            return len(observed)
        for pid in current:
            observed.add(pid)
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        for pid in current:
            try:
                os.waitpid(pid, os.WNOHANG)
            except ChildProcessError:
                pass
        time.sleep(0.01)
    raise RuntimeError("Limpeza incompleta: descarte a VM antes de continuar.")


def invoke(arguments, expected, output=None, max_seconds=None, min_seconds=None,
           pass_fds=(), environment=None):
    start = time.monotonic()
    process = None
    leaks = 0
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            process = subprocess.Popen([str(SUPERVISOR), *arguments], stdout=stdout,
                                       stderr=stderr, start_new_session=True,
                                       pass_fds=pass_fds, env=environment)
            process.wait(timeout=8)
        finally:
            if process is not None and process.poll() is None:
                process.kill()
                process.wait(timeout=2)
            leaks = cleanup_adopted()
        elapsed = time.monotonic() - start
        stdout.seek(0)
        actual_output = stdout.read().decode("utf-8", errors="replace")
        stderr.seek(0)
        diagnostics = stderr.read().decode("utf-8", errors="replace")
    assert process.returncode == expected, (arguments, process.returncode, expected, diagnostics)
    assert leaks == 0, f"{leaks} processos chegaram ao check; o supervisor não recolheu todos"
    if output is not None:
        assert actual_output == output, repr(actual_output)
    if max_seconds is not None:
        assert elapsed < max_seconds, f"{elapsed:.3f}s: revise timeout/limpeza ou carga da VM"
    if min_seconds is not None:
        assert elapsed >= min_seconds, f"{elapsed:.3f}s: timeout antecipado"
    if expected in (2, 124, 125, 126, 127):
        assert "supervisor:" in diagnostics, diagnostics
    print(f"OK status={expected} elapsed={elapsed:.3f}s args={arguments!r}")


def main():
    global SUPERVISOR, PROBE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--supervisor', type=Path, default=SUPERVISOR)
    parser.add_argument('--probe', type=Path, default=PROBE)
    parser.add_argument('--confirm-disposable-vm', action='store_true')
    args = parser.parse_args()
    # Nada de fork, prctl ou limites antes desta guarda.
    require_vm(['--confirm-disposable-vm'] if args.confirm_disposable_vm else [])
    SUPERVISOR, PROBE = args.supervisor.resolve(), args.probe.resolve()
    if not SUPERVISOR.is_file() or not PROBE.is_file():
        raise SystemExit("Compile primeiro: make -C materials")
    as_hard = resource.getrlimit(resource.RLIMIT_AS)[1]
    if as_hard != resource.RLIM_INFINITY and as_hard < 67108864:
        raise SystemExit("Ambiente: hard RLIMIT_AS herdado é menor que 64 MiB.")
    cpu_hard = resource.getrlimit(resource.RLIMIT_CPU)[1]
    if cpu_hard != resource.RLIM_INFINITY and cpu_hard < 1:
        raise SystemExit("Ambiente: hard RLIMIT_CPU herdado é menor que 1 segundo.")
    libc = ctypes.CDLL(None, use_errno=True)
    libc.prctl.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong,
                           ctypes.c_ulong, ctypes.c_ulong]
    libc.prctl.restype = ctypes.c_int
    # O check adota sobras para detectar falhas de reaping e limpá-las.
    if libc.prctl(36, 1, 0, 0, 0) != 0:  # PR_SET_CHILD_SUBREAPER
        raise OSError(ctypes.get_errno(), "PR_SET_CHILD_SUBREAPER")
    try:
        for mode, expected in (("ok", 0), ("exit7", 7), ("term", 143), ("limits", 0)):
            invoke(["1000", "--", str(PROBE), mode], expected, output="")
        for boundary in ("100", "5000"):
            invoke([boundary, "--", str(PROBE), "ok"], 0, output="")
        invoke(["1000", "--", str(PROBE), "args", "two words", "", "; literal"], 0, output="")
        invoke(["1000", "--", str(PROBE), "alloc"], 0, output="allocation=denied\n")
        for mode in ("sleep", "child"):
            invoke(["300", "--", str(PROBE), mode], 124, min_seconds=0.25, max_seconds=1.3)
        invoke(["1000", "--", str(PROBE), "orphan"], 7, max_seconds=1.0)
        for value in ("", "0", "99", "5001", "-1", "+100", "100x", " 100", "9" * 100):
            invoke([value, "--", str(PROBE), "ok"], 2, output="")
        for arguments in ([], ["1000"], ["1000", "--"], ["1000", "x", str(PROBE)],
                          ["1000", "--", ""], ["1000", "--", str(PROBE), "x" * 4097],
                          ["1000", "--", str(PROBE)] + ["x"] * 32):
            invoke(arguments, 2, output="")
        with tempfile.TemporaryDirectory(prefix="oxide-vm-check-") as directory:
            path = Path(directory) / "denied"
            path.write_text("benign fixture\n")
            path.chmod(0)
            try:
                invoke(["1000", "--", str(PROBE), "denied", str(path)], 0, output="file=denied\n")
            finally:
                path.chmod(0o600)
            invoke(["1000", "--", str(path)], 126, output="")
            invoke(["1000", "--", str(Path(directory) / "absent")], 127, output="")
            with path.open() as handle:
                invoke(["1000", "--", str(PROBE), "fd", str(handle.fileno())], 0,
                       output="", pass_fds=(handle.fileno(),))
        unconfirmed = dict(os.environ)
        unconfirmed.pop("OXIDE_DISPOSABLE_VM", None)
        invoke(["1000", "--", str(PROBE), "ok"], 125, output="", environment=unconfirmed)
    finally:
        cleanup_adopted()
    print("Checks públicos concluídos; revise os caminhos de erro e as limitações do contrato.")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, subprocess.TimeoutExpired, RuntimeError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        sys.exit(1)
