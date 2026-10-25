# SPDX-License-Identifier: MIT
"""Regressão Linux: não executa uma implementação dos exercícios."""
import ctypes
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch
import support


class CompilerCleanupTest(unittest.TestCase):
    def test_timeout_terminates_driver_and_child(self):
        self.exercise("timeout")

    def test_interruption_terminates_driver_and_child(self):
        self.exercise("interrupt")

    def exercise(self, mode):
        # O teste torna-se pai dos órfãos próprios para também executar seu reaping.
        libc = ctypes.CDLL(None, use_errno=True)
        previous = ctypes.c_int()
        self.assertEqual(libc.prctl(37, ctypes.byref(previous), 0, 0, 0), 0)
        self.assertEqual(libc.prctl(36, 1, 0, 0, 0), 0)
        ids = []
        real_wait = subprocess.Popen.wait
        try:
            with tempfile.TemporaryDirectory(prefix="compiler-cleanup-") as tmp:
                tmp = Path(tmp)
                marker = tmp / "pids"
                compiler = tmp / "fake-cc"
                compiler.write_text("#!/usr/bin/env python3\n"
                                    "import os, time\n"
                                    "from pathlib import Path\n"
                                    "child = os.fork()\n"
                                    "if child == 0:\n"
                                    "    time.sleep(5)\n"
                                    "else:\n"
                                    f"    Path({str(marker)!r}).write_text(f'{{os.getpid()}} {{child}}')\n"
                                    "    time.sleep(5)\n")
                compiler.chmod(0o700)
                triggered = False

                def controlled_wait(process, timeout=None):
                    nonlocal triggered
                    if timeout is not None and timeout > 10 and not triggered:
                        triggered = True
                        deadline = time.monotonic() + 5
                        while not marker.exists() and time.monotonic() < deadline:
                            time.sleep(0.01)
                        self.assertTrue(marker.exists(), "compilador substituto não iniciou")
                        ids.extend(map(int, marker.read_text().split()))
                        if mode == "interrupt":
                            raise KeyboardInterrupt
                        return real_wait(process, timeout=0.1)
                    return real_wait(process, timeout=timeout)

                expected = KeyboardInterrupt if mode == "interrupt" else subprocess.TimeoutExpired
                started = time.monotonic()
                with patch.dict(os.environ, {"CC": str(compiler)}):
                    with patch.object(subprocess.Popen, "wait", controlled_wait):
                        with self.assertRaises(expected):
                            support.compile_c(tmp / "unused", [])
                self.assertLess(time.monotonic() - started, 2, "interrupção aguardou o compilador terminar sozinho")
                self.assertTrue(triggered)
                with self.assertRaises(ChildProcessError):
                    os.waitpid(ids[0], os.WNOHANG)
                deadline = time.monotonic() + 2
                child_done = False
                while time.monotonic() < deadline:
                    pid, _ = os.waitpid(ids[1], os.WNOHANG)
                    if pid:
                        child_done = True
                        break
                    time.sleep(0.01)
                self.assertTrue(child_done, "subprocesso do compilador continuou vivo")
        finally:
            # O teste também limpa sua árvore quando o helper é defeituoso.
            for pid in ids:
                try:
                    done, _ = os.waitpid(pid, os.WNOHANG)
                except ChildProcessError:
                    continue
                if not done:
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    os.waitpid(pid, 0)
            self.assertEqual(libc.prctl(36, previous.value, 0, 0, 0), 0)


if __name__ == "__main__":
    unittest.main()
