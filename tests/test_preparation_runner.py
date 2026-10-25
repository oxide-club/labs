"""SPDX-License-Identifier: MIT"""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/verify-preparation.py'
class PreparationRunnerTests(unittest.TestCase):
    def module(self):
        self.assertTrue(SCRIPT.exists(), 'runner de preparação ainda ausente')
        spec=importlib.util.spec_from_file_location('preparation',SCRIPT)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module
    def test_expected_failure_is_not_confused_with_broken_command(self):
        module=self.module()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            check={'name':'incompleto','argv':[sys.executable,'-c','print("INCOMPLETO"); raise SystemExit(1)'],
                   'status':1,'contains':'INCOMPLETO'}
            self.assertTrue(module.run_check(root,root,check)['ok'])
            check['contains']='outra saída'
            self.assertFalse(module.run_check(root,root,check)['ok'])
            check['argv']=['/oxide-no-such-program']
            self.assertFalse(module.run_check(root,root,check)['ok'])
    def test_timeout_is_failure_even_for_intentional_nonzero_exit(self):
        module=self.module()
        with tempfile.TemporaryDirectory() as d:
            check={'name':'bloqueado','argv':[sys.executable,'-c','import time; time.sleep(30)'],
                   'status':1,'timeout':0.1}
            result=module.run_check(Path(d),Path(d),check)
            self.assertFalse(result['ok']); self.assertEqual(result['reason'],'timeout')
if __name__=='__main__':unittest.main()
