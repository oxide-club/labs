# SPDX-License-Identifier: MIT
"""MIT. Regressão de diagnósticos: falhas de execução não expõem entradas."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CHECK = Path(__file__).with_name("check.py")
SENTINEL = b"Z9!q4?"


class DiagnosticTests(unittest.TestCase):
    def invoke(self, binary, candidate):
        return subprocess.run(
            [sys.executable, str(CHECK), str(binary), "--accepted-file", str(candidate)],
            capture_output=True, timeout=15)

    def assert_private_failure(self, result, message):
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(SENTINEL not in result.stdout + result.stderr,
                        "a falha expôs a entrada sentinela")
        self.assertTrue(b"Traceback" not in result.stderr,
                        "a falha imprimiu traceback")
        self.assertTrue(message in result.stderr, "diagnóstico fixo ausente")

    def test_timeout_omits_candidate(self):
        with tempfile.TemporaryDirectory(prefix="gate-check-test-") as directory:
            root = Path(directory)
            candidate = root / "candidate.bin"
            candidate.write_bytes(SENTINEL)
            binary = root / "slow-target"
            binary.write_text(
                "#!" + sys.executable + "\n"
                "import sys, time\n"
                "if len(sys.argv) != 2:\n"
                "    print('uso: ' + sys.argv[0] + ' CHAVE', file=sys.stderr)\n"
                "    sys.exit(2)\n"
                "if sys.argv[1].encode() == " + repr(SENTINEL) + ":\n"
                "    time.sleep(30)\n"
                "print('porta fechada')\n"
                "sys.exit(1)\n")
            binary.chmod(0o700)
            result = self.invoke(binary, candidate)
            self.assertTrue("6 casos públicos: OK".encode() in result.stdout,
                            "o alvo não alcançou a verificação do candidato")
            self.assert_private_failure(result, b"limite de execu")

    def test_execution_oserror_omits_arguments(self):
        with tempfile.TemporaryDirectory(prefix="gate-check-test-") as directory:
            root = Path(directory)
            candidate = root / "candidate.bin"
            candidate.write_bytes(SENTINEL)
            # O nome sentinel também não deve vazar pelo texto de OSError.
            binary = root / SENTINEL.decode()
            result = self.invoke(binary, candidate)
            self.assert_private_failure(result, b"executar o alvo")


if __name__ == "__main__":
    unittest.main()
