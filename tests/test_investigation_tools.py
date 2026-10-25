"""SPDX-License-Identifier: MIT
Instrumentos devem distinguir representações e capturar diagnósticos reais.
"""
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InvestigationToolsTests(unittest.TestCase):
    def test_external_bytes_and_wrong_endian_are_independent_of_host(self):
        source = ROOT / '001-binary-lab/materials/experiments/representation.c'
        with tempfile.TemporaryDirectory() as tmp:
            binary = str(Path(tmp) / 'representation')
            result = subprocess.run(shlex.split(os.environ.get('CC', 'cc')) + [
                '-std=c11', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                '-fsanitize=undefined', '-fno-sanitize-recover=all',
                str(source), '-o', binary], capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run([binary], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, '')
            self.assertIn('LE=04 03 02 01 BE=01 02 03 04 wrong=0x04030201', result.stdout)
            self.assertIn('LE=02 01 50 22 BE=22 50 01 02 wrong=0x02015022', result.stdout)
            self.assertIn('LE=FF FF FF FF BE=FF FF FF FF wrong=0xFFFFFFFF', result.stdout)
            self.assertIn('logical_equal=1 external_equal=1 external=07 04 03 02 01 06 05', result.stdout)

    def test_memory_comparison_records_controls_and_real_uaf(self):
        script = ROOT / '003-memory-safety-lab/materials/experiments/compare.py'
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'evidence'
            result = subprocess.run(['python3', str(script), str(output)],
                                    capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads((output / 'results.json').read_text())
            self.assertEqual(set(data['cases']), {'borrowed', 'owner-null', 'copy', 'reset'})
            for name in ('borrowed', 'copy', 'reset'):
                self.assertEqual(data['cases'][name]['status'], 0)
                self.assertEqual((output / (name + '.stderr')).read_text(), '')
            self.assertIn('Club', (output / 'copy.stdout').read_text())
            self.assertIn('heap-use-after-free', (output / 'owner-null.stderr').read_text())
            self.assertNotEqual(data['cases']['owner-null']['status'], 0)
            reset = (output / 'reset.stdout').read_text()
            self.assertIn('old_generation=1 current_generation=2', reset)
            self.assertIn('old_handle_valid=0 addressable=Rust', reset)
            # Reexecutar não pode sobrescrever evidência anterior.
            saved = (output / 'results.json').read_bytes()
            retry = subprocess.run(['python3', str(script), str(output)],
                                   capture_output=True, timeout=10)
            self.assertNotEqual(retry.returncode, 0)
            self.assertEqual((output / 'results.json').read_bytes(), saved)


if __name__ == '__main__':
    unittest.main()
