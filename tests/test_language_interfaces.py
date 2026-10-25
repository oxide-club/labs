"""SPDX-License-Identifier: MIT — regressões da seleção de implementações."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LanguageInterfaces(unittest.TestCase):
    def test_vm_transport_preserves_source_budget_and_state(self):
        spec = importlib.util.spec_from_file_location('vm_check', ROOT/'009-vm-lab/checks/check.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory)/'transport'
            # Fixture de transporte, não interpretador: confere bytes/argv e retorna dado fixo.
            executable.write_text('#!/usr/bin/env python3\nimport json,sys\n'
                                  'assert sys.argv[1] == "3"\n'
                                  'assert sys.stdin.read() == "PUSH 2\\nHALT\\n"\n'
                                  'print(json.dumps({"stack": [2], "error": None}))\n')
            executable.chmod(0o700)
            self.assertEqual(module.ExecutableVM(executable).run('PUSH 2\nHALT\n', 3),
                             {'stack': [2], 'error': None})

    def test_vm_transport_rejects_python_budget_types_before_serialization(self):
        spec = importlib.util.spec_from_file_location('vm_check', ROOT/'009-vm-lab/checks/check.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        vm = module.ExecutableVM('/must-not-execute')
        for value in ('2', True, None, 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                vm.run('HALT', value)

    def test_isolation_external_path_does_not_bypass_vm_guard(self):
        result = subprocess.run([sys.executable, str(ROOT/'016-isolation-lab/checks/check.py'),
                                 '--supervisor', '/does-not-exist'],
                                text=True, capture_output=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('VM descartável', result.stderr)
        self.assertNotIn('unrecognized arguments', result.stderr)

    def test_go_sources_distributed_but_artifacts_excluded(self):
        spec = importlib.util.spec_from_file_location('validate', ROOT/'scripts/validate.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(module.distributed(Path('materials/starter/go/protocol.go')))
        self.assertTrue(module.distributed(Path('materials/starter/go/go.mod')))
        self.assertFalse(module.distributed(Path('materials/starter/go/build/protocol')))

    def test_vm_executable_is_actually_invoked(self):
        # Um executável que falha precisa reprovar, sem cair no import Python.
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory)/'participant'
            executable.write_text('#!/bin/sh\necho external-vm-sentinel >&2\nexit 7\n')
            executable.chmod(0o700)
            result = subprocess.run([sys.executable, str(ROOT/'009-vm-lab/checks/check.py'),
                                     str(executable)], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 1)
        self.assertIn('external-vm-sentinel', result.stderr)
        self.assertNotIn('NotImplementedError', result.stderr)


if __name__ == '__main__':
    unittest.main()
